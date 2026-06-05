"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import { Send, Paperclip, Mic } from "lucide-react";

export default function ChatWindow() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { id: 1, role: "system", content: "أهلاً بك في نظام قيام. أنا مستعد لتحليل البيانات، كتابة التقارير، واتخاذ القرارات الاستراتيجية. كيف يمكنني مساعدتك اليوم؟" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { id: Date.now(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      // Connect to FastAPI Backend
      const response = await fetch("http://127.0.0.1:8000/api/v1/invoke", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.content, user_id: "admin" })
      });
      
      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        role: "assistant", 
        content: data.response || "عذراً، حدث خطأ أثناء المعالجة." 
      }]);
    } catch (error: any) {
      console.error(error);
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        role: "assistant", 
        content: `خطأ تقني: ${error.message || error.toString()} \n يرجى التحقق من نافذة (CMD) الخاصة بالخادم (FastAPI) لمعرفة التفاصيل.` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
        ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-primary opacity-70">
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
            <span className="text-sm mr-2">جاري المعالجة والتحليل...</span>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-surface border-t border-border">
        <div className="max-w-4xl mx-auto relative flex items-center bg-background border border-border rounded-xl focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all">
          <button className="p-3 text-gray-400 hover:text-primary transition-colors">
            <Paperclip size={20} />
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="اكتب رسالتك أو اطلب تحليلاً..."
            className="flex-1 bg-transparent border-none outline-none py-4 px-2 text-white placeholder-gray-500"
            disabled={isLoading}
          />
          <button className="p-3 text-gray-400 hover:text-primary transition-colors">
            <Mic size={20} />
          </button>
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="m-2 p-2 bg-primary text-black rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
