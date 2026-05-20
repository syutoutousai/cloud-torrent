'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
    LayoutDashboard, 
    DownloadCloud, 
    PlayCircle, 
    Settings, 
    History,
    Search
} from 'lucide-react';

const SidebarItem = ({ icon: Icon, label, active = false }: { icon: any, label: string, active?: boolean }) => (
    <motion.div 
        whileHover={{ x: 5 }}
        className={`flex items-center gap-3 px-4 py-3 cursor-pointer rounded-lg transition-all ${
            active 
            ? 'bg-primary/10 text-primary border-l-4 border-primary' 
            : 'text-foreground/60 hover:text-foreground hover:bg-white/5'
        }`}
    >
        <Icon size={20} />
        <span className="font-medium">{label}</span>
    </motion.div>
);

export const Sidebar = () => {
    return (
        <aside className="w-64 h-screen border-r border-border bg-card/50 backdrop-blur-xl flex flex-col p-4 gap-2">
            <div className="flex items-center gap-3 px-4 mb-8">
                <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(0,212,255,0.3)]">
                    <DownloadCloud className="text-background" size={24} />
                </div>
                <h1 className="text-xl font-bold tracking-tight text-foreground">
                    CLOUD <span className="text-primary">V2</span>
                </h1>
            </div>

            <div className="flex-1 flex flex-col gap-1">
                <SidebarItem icon={LayoutDashboard} label="Dashboard" active />
                <SidebarItem icon={PlayCircle} label="Streaming" />
                <SidebarItem icon={Search} label="Indexers" />
                <SidebarItem icon={History} label="History" />
            </div>

            <div className="mt-auto pt-4 border-t border-border">
                <SidebarItem icon={Settings} label="Settings" />
            </div>
        </aside>
    );
};
