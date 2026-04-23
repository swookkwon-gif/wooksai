"use client";

import { useState } from "react";
import { askCopilot, publishPost, loadYoonsAiData } from "./actions";
import { Send, Sparkles, BookCheck, ArrowLeft, Download } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "model";
  text: string;
}

export default function AdminCopilot() {
  const [category, setCategory] = useState("AI 뉴스 모음 및 자평");
  const [topic, setTopic] = useState("");
  const [input, setInput] = useState("");
  const [chat, setChat] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessageToCopilot = async (userText: string) => {
    const userMessage: Message = { role: "user", text: userText };
    setChat((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const history = chat.map((msg) => ({
      role: msg.role,
      parts: [{ text: msg.text }],
    }));

    const result = await askCopilot(topic, category, userMessage.text, history);

    if (result.success && result.text) {
      setChat((prev) => [...prev, { role: "model", text: result.text }]);
    } else {
      setChat((prev) => [
        ...prev,
        { role: "model", text: "오류가 발생했습니다: " + result.error },
      ]);
    }
    setIsLoading(false);
  };

  const handleSend = () => {
    if (!input.trim() || !topic.trim()) return;
    const textToSend = input;
    setInput("");
    sendMessageToCopilot(textToSend);
  };

  const handleLoadYoonsAi = async () => {
    if (!topic.trim()) {
      return alert("먼저 주제(Topic)를 간략히 입력해주세요.");
    }
    setIsLoading(true);
    const result = await loadYoonsAiData();
    if (result.success && result.data) {
      const prompt = `다음은 오늘자 Yoon's AI 뉴스레터 내용입니다. 이를 읽고 블로그 포스팅용 초안을 먼저 작성해서 보여줘. 
내용:
${result.data}`;
      await sendMessageToCopilot(prompt);
    } else {
      alert("데이터 불러오기 실패: " + result.error);
    }
    setIsLoading(false);
  };

  const handlePublish = async () => {
    const modelMessages = chat.filter((msg) => msg.role === "model");
    if (modelMessages.length === 0) return alert("발행할 초안이 없습니다.");

    const lastDraft = modelMessages[modelMessages.length - 1].text;
    const result = await publishPost(topic, category, lastDraft);

    if (result.success) {
      alert(`[${result.filename}] 포스팅이 성공적으로 발행되었습니다!`);
    } else {
      alert("발행 실패: " + result.error);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 font-sans flex flex-col h-screen">
      <header className="flex items-center justify-between py-4 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-neutral-400 hover:text-white transition-colors">
            <ArrowLeft size={20} />
          </Link>
          <h1 className="text-xl font-bold font-outfit text-gradient flex items-center gap-2">
            <Sparkles size={20} className="text-violet-400" /> AI Editor Copilot
          </h1>
        </div>
        <button
          onClick={handlePublish}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm font-bold transition-all"
        >
          <BookCheck size={16} /> 블로그 발행하기
        </button>
      </header>

      {/* Settings Row */}
      <div className="flex gap-4 py-4 shrink-0">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-violet-500"
        >
          <option value="AI News Flood">1. AI News Flood (Yoon's AI 연동)</option>
          <option value="마케팅 논문 하나 읽고 허리 펴기">2. 마케팅 논문 하나 읽고 허리 펴기</option>
          <option value="Career">3. Career</option>
        </select>
        
        <input
          type="text"
          placeholder="오늘 다룰 구체적인 주제 또는 분석할 URL"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-violet-500 placeholder-neutral-500"
        />

        {category.includes("News") && (
          <button
            onClick={handleLoadYoonsAi}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 border border-blue-500/30 rounded-lg text-sm font-bold transition-all disabled:opacity-50 whitespace-nowrap"
          >
            <Download size={16} /> Yoon's AI 불러오기
          </button>
        )}
        
        {category.includes("논문") && (
          <button
            onClick={() => sendMessageToCopilot("오늘의 논문을 추천해주고 제안해줘!")}
            disabled={isLoading || !topic.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-green-600/20 text-green-400 hover:bg-green-600/30 border border-green-500/30 rounded-lg text-sm font-bold transition-all disabled:opacity-50 whitespace-nowrap"
          >
            <Sparkles size={16} /> 논문 추천받기
          </button>
        )}
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6 scrollbar-hide">
        {chat.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-neutral-500">
            <Sparkles size={48} className="mb-4 opacity-20" />
            <p>주제를 입력하고 대화를 시작하세요.</p>
            <p className="text-sm mt-2 max-w-lg text-center leading-relaxed">
              * Yoon's AI 뉴스 모드: 상단의 [불러오기] 버튼 클릭<br />
              * 논문 리뷰 모드: 상단의 [AI 추천받기] 버튼 클릭<br />
              그 외 카테고리는 하단에 대화를 바로 시작하시면 편집장이 인계를 리드합니다.
            </p>
          </div>
        ) : (
          chat.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-5 ${
                  msg.role === "user"
                    ? "bg-violet-600 border border-violet-500 text-white"
                    : "bg-white/5 border border-white/10"
                }`}
              >
                {msg.role === "model" ? (
                  <div className="prose prose-invert prose-violet max-w-none prose-sm sm:prose-base">
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-neutral-400 flex items-center gap-2">
              <span className="animate-pulse">AI 편집장이 작업 중입니다...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="pt-4 shrink-0 mt-auto">
        <div className="flex gap-2 bg-white/5 border border-white/10 p-2 rounded-xl focus-within:border-violet-500 transition-colors">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="AI 편집장에게 답변을 입력하세요. (Shift+Enter로 줄바꿈)"
            className="flex-1 bg-transparent resize-none outline-none py-2 px-3 text-sm max-h-32 focus:ring-0"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:hover:bg-violet-600 rounded-lg transition-all self-end"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
