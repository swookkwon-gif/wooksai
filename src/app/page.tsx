import { ArrowRight, BookOpen, Newspaper, BrainCircuit, BookType, Sparkles, Target, Briefcase } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const categories = [
    {
      id: 1,
      title: "AI News Flood",
      description: "Yoon's AI가 매일 요약하는 글로벌 AI 동향 및 최신 비즈니스 비평",
      icon: <Newspaper className="text-white" size={24} />,
    },
    {
      id: 2,
      title: "마케팅 논문 하나 읽고 허리 펴기",
      description: "마케팅 사이언스와 최신 AI/데이터 관련 저명 논문 데일리 리뷰",
      icon: <BookType className="text-white" size={24} />,
    },
    {
      id: 3,
      title: "Career",
      description: "AI 시대 마케터의 기획, 성장, 리더십 가이드와 회고",
      icon: <Briefcase className="text-white" size={24} />,
    },
  ];

  return (
    <main className="min-h-screen px-6 pt-32 pb-24 max-w-6xl mx-auto font-sans">
      {/* Hero Section */}
      <section className="mb-24 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 text-sm font-medium border rounded-full bg-white/5 border-white/10 text-violet-400">
          <Sparkles size={14} />
          <span>Automated Insights & Curation</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 font-outfit text-gradient leading-tight">
          Wook's <br />
          <span className="text-violet-500">AI and Marketing</span>
        </h1>
        <p className="text-lg md:text-xl text-neutral-400 mb-10 max-w-2xl mx-auto leading-relaxed">
          AI와 디지털 마케팅의 융합. 기술 트렌드부터 학술 논문, 그리고 커리어 인사이트까지 
          폭넓은 지식을 큐레이션합니다.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/posts"
            className="px-8 py-3 rounded-full primary-gradient font-semibold hover:opacity-90 active:scale-95 transition-all flex items-center gap-2"
          >
            최신 포스팅 보기 <ArrowRight size={18} />
          </Link>
          <button className="px-8 py-3 rounded-full glass-card font-semibold hover:bg-white/10 transition-all">
            소개 보기
          </button>
        </div>
      </section>

      {/* Categories Grid */}
      <section className="mb-20">
        <h2 className="text-2xl font-bold mb-8 font-outfit tracking-wide text-white/90">Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((cat) => (
            <div key={cat.id} className="glass-card p-8 group cursor-pointer">
              <div className="w-12 h-12 rounded-xl primary-gradient flex items-center justify-center mb-6 shadow-lg shadow-violet-500/20 transform group-hover:scale-110 transition-transform">
                {cat.icon}
              </div>
              <h3 className="text-xl font-bold mb-3 font-outfit">{cat.title}</h3>
              <p className="text-neutral-400 leading-relaxed text-sm">
                {cat.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-32 pt-12 border-t border-white/5 text-center text-neutral-600 text-sm">
        © 2026 Wook's AI and Marketing. Built with Next.js & Automated by AI.
      </footer>
    </main>
  );
}
