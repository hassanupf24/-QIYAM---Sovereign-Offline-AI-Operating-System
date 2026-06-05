import { MessageSquare, BarChart2, Settings, HardDrive, Shield } from "lucide-react";

export default function Sidebar({ activeTab, setActiveTab }: { activeTab: string, setActiveTab: (t: string) => void }) {
  const menuItems = [
    { id: "chat", label: "المحادثة", icon: <MessageSquare size={20} /> },
    { id: "insights", label: "الرؤى والتحليلات", icon: <BarChart2 size={20} /> },
    { id: "memory", label: "الذاكرة المعرفية", icon: <HardDrive size={20} /> },
    { id: "security", label: "سجل الأمان", icon: <Shield size={20} /> },
    { id: "settings", label: "الإعدادات", icon: <Settings size={20} /> },
  ];

  return (
    <aside className="w-64 bg-surface border-l border-border h-full flex flex-col">
      <div className="p-6">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          QIYAM OS
        </h2>
        <p className="text-xs text-gray-400 mt-1">Enterprise AI System v2.0</p>
      </div>

      <nav className="flex-1 px-4 mt-4 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeTab === item.id 
                ? "bg-primary/10 text-primary border border-primary/20" 
                : "text-gray-400 hover:bg-surfaceHover hover:text-white"
            }`}
          >
            {item.icon}
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="bg-surfaceHover p-4 rounded-lg">
          <p className="text-xs text-gray-400 mb-2">Memory Usage</p>
          <div className="w-full bg-background rounded-full h-2">
            <div className="bg-primary h-2 rounded-full" style={{ width: '45%' }}></div>
          </div>
          <p className="text-xs text-right mt-1 text-gray-500">45% (SQLite + Chroma)</p>
        </div>
      </div>
    </aside>
  );
}
