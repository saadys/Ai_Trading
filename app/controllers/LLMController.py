from fastapi import HTTPException
from app.core.logger import logger
from app.stores.LLM.LLMProviderFactory import LLMProviderFactory
from app.stores.LLM.LLMEnum import LLMEnum
from app.core.config import get_settings

class LLMController:
    def __init__(self, app_instance):
        self.app = app_instance
        self.settings = get_settings()

    async def Trigger_Decision(self):
        try:
            logger.info("[LLMController] Déclenchement manuel d'une décision LLM...")
            
            context = getattr(self.app, "context_aggregator", None)
            if not context:
                raise HTTPException(status_code=500, detail="ContextAggregator non initialisé.")
            
            context_data = context.aggregate_functions()
            if not context_data:
                logger.warning("[LLMController] Contexte marché vide.")
                raise HTTPException(status_code=400, detail="Contexte vide, impossible de prendre une décision.")

            # 2. Construction du Prompt
            prompt_text = self.app.prompt_builder.Construire_Prompt(context_data)

            # 3. Appel au LLM actif
            decision = await self.app.llm_provider.aggregate_responses(prompt_text)

            if decision:
                final = self.app.llm_provider.Text_To_JSON(decision) if isinstance(decision, str) else decision
                logger.info(f"[LLMController] Décision forcée générée avec succès : {final.get('action')}")
                return final
            else:
                raise HTTPException(status_code=502, detail="Aucune réponse valide reçue du provider LLM.")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[LLMController] Erreur fatale dans Trigger_Decision : {e}")
            raise HTTPException(status_code=500, detail=str(e))
    #        Renvoie le contexte actuel aggrégé (JSON) pour l'audit et le debug.
    def Get_Current_Context(self):

        try:
            context = getattr(self.app, "context_aggregator", None)
            if not context:
                raise HTTPException(status_code=500, detail="ContextAggregator non initialisé.")
                
            context_data = context.aggregate_functions()
            if not context_data:
                return {"message": "Le contexte est actuellement vide (les données arrivent...)."}
            
            return context_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[LLMController] Erreur dans Get_Current_Context : {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    #Change dynamiquement le provider LLM actif ( GEMINI -> DEEPSEEK) .
    def Change_Provider(self, provider_name: str):
        try:
            # Recherche de l'Enum correspondant ignorée la casse (Deepseek, deepseek, DEEPSEEK...)
            enum_member = None
            for p in LLMEnum:
                if p.name.upper() == provider_name.upper():
                    enum_member = p
                    break
            
            if not enum_member:
                valid_options = [p.name for p in LLMEnum]
                raise HTTPException(
                    status_code=400, 
                    detail=f"Provider non supporté : '{provider_name}'. Options valides : {valid_options}"
                )
            
            new_provider = LLMProviderFactory(self.settings).create(enum_member)
            
            self.app.llm_provider = new_provider
            
            logger.info(f"[LLMController] Provider LLM changé avec succès vers {enum_member.name}")
            return {"message": f"Provider LLM changé avec succès vers {enum_member.name}"}
            
        except NotImplementedError as ne:
            logger.warning(f"[LLMController] Provider pas encore implémenté : {ne}")
            raise HTTPException(status_code=501, detail=str(ne))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[LLMController] Erreur inattendue dans Change_Provider : {e}")
            raise HTTPException(status_code=500, detail=str(e))
