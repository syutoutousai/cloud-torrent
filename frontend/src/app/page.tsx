import React from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Search, Plus, Zap } from 'lucide-react';

export default function Home() {
  return (
    <main className="flex min-h-screen bg-background">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Top Nav / Search */}
        <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-card/30 backdrop-blur-md sticky top-0 z-10">
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-foreground/40" size={18} />
            <input 
              type="text" 
              placeholder="Paste magnet link or search..." 
              className="w-full bg-white/5 border border-border rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary/50 transition-all"
            />
          </div>
          
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 bg-primary text-background px-4 py-2 rounded-full font-bold text-sm shadow-[0_0_15px_rgba(0,212,255,0.2)] hover:scale-105 transition-transform">
              <Plus size={18} />
              Add Torrent
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-8 space-y-8 overflow-y-auto">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-foreground">Active Swarm</h2>
              <p className="text-foreground/50 mt-1">Real-time health of your local streams.</p>
            </div>
            
            <div className="flex gap-4">
              <div className="glass px-6 py-4 rounded-2xl flex flex-col items-end">
                <span className="text-xs text-foreground/40 uppercase tracking-widest font-bold">Total Down</span>
                <span className="text-2xl font-mono text-primary flex items-center gap-2">
                  <Zap size={20} className="fill-primary" />
                  24.5 MB/s
                </span>
              </div>
            </div>
          </div>

          {/* Placeholder for Torrent List */}
          <div className="grid grid-cols-1 gap-4">
            {[1, 2].map((i) => (
              <div key={i} className="glass p-6 rounded-2xl glow-blue transition-all group">
                <div className="flex items-start justify-between">
                  <div className="flex gap-4">
                    <div className="w-12 h-16 bg-white/5 rounded-lg flex items-center justify-center text-foreground/20 italic">
                      POSTER
                    </div>
                    <div>
                      <h3 className="text-xl font-bold group-hover:text-primary transition-colors">Yellowstone S04E03 - All I See Is You</h3>
                      <div className="flex items-center gap-4 mt-2 text-sm text-foreground/40">
                        <span>1.4 GB / 2.1 GB</span>
                        <span className="w-1 h-1 bg-border rounded-full" />
                        <span className="text-green-500 font-bold">128 Seeds</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <button className="p-2 hover:bg-white/10 rounded-full transition-colors text-foreground/60 hover:text-foreground">
                      <Zap size={20} />
                    </button>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-6 relative h-2 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="absolute inset-0 bg-gradient-to-r from-primary to-primary/40 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(0,212,255,0.5)]"
                    style={{ width: i === 1 ? '68%' : '32%' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
