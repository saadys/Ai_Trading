import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "@/components/landing/Navbar";
import MarketChart from "@/components/dashboard/MarketChart";
import MarketDataList from "@/components/dashboard/MarketDataList";
import StatsOverview from "@/components/dashboard/StatsOverview";
import PredictAction from "@/components/dashboard/PredictAction";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <div className="p-6 md:p-12 max-w-7xl mx-auto">
        <header className="flex items-center mb-8 gap-4 border-b border-border/50 pb-6">
        <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Trading Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Test the AI trading model on simulated historical data.
          </p>
        </div>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content: Chart and History */}
        <div className="lg:col-span-2 space-y-6">
          <MarketChart />
          <MarketDataList />
        </div>
        
        {/* Sidebar: Stats and Action */}
        <div className="space-y-6">
          <StatsOverview />
          <PredictAction />
        </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
