import { User, Bot, ShieldAlert } from "lucide-react";

interface MessageProps {
  role: string;
  content: string;
}

export default function MessageBubble({ role, content }: MessageProps) {
  const isUser = role === "user";
  const isSystem = role === "system";
  
  return (
    <div className={`flex gap-4 max-w-4xl w-full mx-auto ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
        isUser ? "bg-secondary text-black" : 
        isSystem ? "bg-primary text-black" : 
        "bg-red-500 text-white" // For Security alerts
      }`}>
        {isUser ? <User size={24} /> : isSystem ? <Bot size={24} /> : <ShieldAlert size={24} />}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[80%]`}>
        <span className="text-xs text-gray-400 mb-1 px-1">
          {isUser ? "أنت" : isSystem ? "نظام قيام (المراقب)" : "تنبيه أمني"}
        </span>
        <div className={`p-4 rounded-2xl ${
          isUser 
            ? "bg-surface border border-border rounded-tr-sm" 
            : "bg-primary/10 border border-primary/20 text-blue-50 rounded-tl-sm"
        }`}>
          {/* Simple text rendering. In production, use React Markdown here */}
          <p className="leading-relaxed whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    </div>
  );
}
