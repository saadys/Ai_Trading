import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const faqs = [
  { q: "How accurate is Vibe Trade's analysis?", a: "Our AI achieves an average accuracy of 87% across all pattern types, validated against historical market data." },
  { q: "Can I use Vibe Trade for different trading styles?", a: "Absolutely! Vibe Trade supports swing trading, day trading, scalp trading, and position trading strategies." },
  { q: "What markets does Vibe Trade support?", a: "We support stocks, forex, crypto, futures, and options across all major exchanges worldwide." },
  { q: "How do I cancel my subscription?", a: "You can cancel anytime from your account settings. No questions asked, no hidden fees." },
  { q: "Is my trading data secure?", a: "Yes. All data is encrypted end-to-end using bank-grade AES-256 encryption and stored securely." },
];

const FAQ = () => (
  <div id="faq" className="section-block-alt">
    <div className="section-block-alt-inner">
      <div className="section-header">
        <p className="section-tag">FAQ</p>
        <h2 className="section-title">Questions? Answers.</h2>
      </div>
      <div className="faq-container">
        <Accordion type="single" collapsible className="space-y-3">
          {faqs.map((f, i) => (
            <AccordionItem key={i} value={`item-${i}`} className="glass-card px-6 border-none">
              <AccordionTrigger className="text-sm font-semibold text-foreground hover:no-underline">{f.q}</AccordionTrigger>
              <AccordionContent className="text-sm text-muted-foreground">{f.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  </div>
);

export default FAQ;
