import { Activity, Database, Briefcase, Zap, CheckCircle2 } from "lucide-react";

export default function AgentStatus() {
  const agents = [
    { name: "Meta-Agent (Orchestrator)", status: "Active", icon: <Zap size={16} />, color: "text-yellow-400" },
    { name: "Data Analyst", status: "Idle", icon: <Database size={16} />, color: "text-blue-400" },
    { name: "Business Intelligence", status: "Idle", icon: <Briefcase size={16} />, color: "text-purple-400" },
    { name: "Security Guard", status: "Monitoring", icon: <CheckCircle2 size={16} />, color: "text-green-400" }
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <Activity size={20} className="text-primary" />
          حالة الوكلاء (Agents)
        </h3>
      </div>
      
      <div className="p-4 flex-1 overflow-y-auto space-y-4">
        {agents.map((agent, i) => (
          <div key={i} className="bg-background p-3 rounded-lg border border-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-md bg-surfaceHover ${agent.color}`}>
                {agent.icon}
              </div>
              <div>
                <p className="text-sm font-medium">{agent.name}</p>
                <p className="text-xs text-gray-400 flex items-center gap-1">
                  <span className={`w-1.5 h-1.5 rounded-full ${agent.status === 'Active' || agent.status === 'Monitoring' ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                  {agent.status}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-border bg-surfaceHover mt-auto">
        <h4 className="text-sm font-medium mb-2">التنفيذ الأخير (Execution Trace)</h4>
        <div className="text-xs text-gray-400 space-y-2 font-mono">
          <p className="text-green-400">{">"} Intent: general_chat (94%)</p>
          <p>{">"} Routing: Meta-Agent → User</p>
          <p>{">"} Memory: Read (2ms)</p>
          <p>{">"} Security: PASS (Risk 0.0)</p>
          <p>{">"} Latency: 450ms</p>
        </div>
      </div>
    </div>
  );
}
