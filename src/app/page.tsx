import { ArrowRight, Newspaper, BookType, Sparkles, Briefcase } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const categories = [
    {
      id: 1,
      title: "AI News Flood",
      description: "Yoon's AI가 매일 요약하는 글로벌 AI 동향 및 최신 비즈니스 비평",
      icon: <Newspaper className="text-neutral-800" size={24} />,
    },
    {
      id: 2,
      title: "마케팅 논문 하나 읽고 허리 펴기",
      description: "마케팅 사이언스와 최신 AI/데이터 관련 저명 논문 데일리 리뷰",
      icon: <BookType className="text-neutral-800" size={24} />,
    },
    {
      id: 3,
      title: "Career",
      description: "AI 시대 마케터의 기획, 성장, 리더십 가이드와 회고",
      icon: <Briefcase className="text-neutral-800" size={24} />,
    },
  ];

  return (
    <main className="min-h-screen px-6 pt-32 pb-24 max-w-5xl mx-auto font-sans bg-white">
      {/* Hero Section */}
      <section className="mb-28 text-center md:text-left">
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 text-xs font-semibold border rounded-full bg-neutral-50 border-neutral-200 text-neutral-600 uppercase tracking-widest">
          <Sparkles size={12} />
          <span>Automated Insights & Curation</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 text-neutral-900 leading-tight">
          Wook&apos;s <br />
          <span className="text-blue-600">AI and Marketing</span>
        </h1>
        <p className="text-lg md:text-xl text-neutral-500 mb-12 max-w-2xl leading-relaxed">
          AI와 디지털 마케팅의 융합. 기술 트렌드부터 학술 논문, 그리고 커리어 인사이트까지 
          폭넓은 지식을 정갈하게 큐레이션합니다.
        </p>
        <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
          <Link
            href="/posts"
            className="px-8 py-3.5 rounded-full bg-neutral-900 text-white font-semibold hover:bg-neutral-800 active:scale-95 transition-all flex items-center gap-2 text-sm"
          >
            블로그 아티클 보기 <ArrowRight size={16} />
          </Link>
          <button className="px-8 py-3.5 rounded-full bg-white text-neutral-900 border border-neutral-200 font-semibold hover:bg-neutral-50 transition-all text-sm">
            소개 보기
          </button>
        </div>
      </section>

      {/* Categories Grid */}
      <section className="mb-24">
        <h2 className="text-2xl font-bold mb-10 tracking-tight text-neutral-900">카테고리</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((cat) => (
            <div key={cat.id} className="clean-card p-8 group">
              <div className="w-12 h-12 rounded-xl bg-neutral-100 flex items-center justify-center mb-6 group-hover:bg-blue-50 transition-colors">
                {cat.icon}
              </div>
              <h3 className="text-xl font-bold mb-3 text-neutral-900">{cat.title}</h3>
              <p className="text-neutral-500 leading-relaxed text-sm">
                {cat.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-32 pt-12 border-t border-neutral-100 text-center md:text-left text-neutral-400 text-sm flex flex-col md:flex-row justify-between items-center gap-4">
        <p>© 2026 Wook&apos;s AI and Marketing. All rights reserved.</p>
        <p>Built with Next.js & Automated by AI.</p>
      </footer>
    </main>
  );
}
