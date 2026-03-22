import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import TradingViewSection from "@/components/landing/TradingViewSection";
import Stats from "@/components/landing/Stats";
import LogoTicker from "@/components/landing/LogoTicker";
import MarketNews from "@/components/landing/MarketNews";
import HowItWorks from "@/components/landing/HowItWorks";
import Features from "@/components/landing/Features";
import Pricing from "@/components/landing/Pricing";
import FAQ from "@/components/landing/FAQ";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";

const Index = () => (
  <div className="min-h-screen bg-background">
    <Navbar />
    <Hero />
    <TradingViewSection />
    <LogoTicker />
    <MarketNews />
    <HowItWorks />
    <Features />
    <Pricing />
    <FAQ />
    <CTASection />
    <Footer />
  </div>
);

export default Index;
