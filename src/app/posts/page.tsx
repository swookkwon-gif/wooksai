import { getSortedPostsData } from "@/lib/posts";
import Link from "next/link";
import { ArrowLeft, Calendar, Tag } from "lucide-react";

export default function PostsPage() {
  const posts = getSortedPostsData();

  return (
    <main className="min-h-screen px-6 pt-24 pb-24 max-w-4xl mx-auto font-sans">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-neutral-400 hover:text-white mb-12 transition-colors group"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        홈으로 돌아가기
      </Link>

      <header className="mb-16">
        <h1 className="text-4xl font-bold font-outfit mb-4 text-gradient">AI Insight Reports</h1>
        <p className="text-neutral-400">AI가 분석한 최신 트렌드와 리포트를 확인하세요.</p>
      </header>

      <div className="space-y-8">
        {posts.map((post) => (
          <article key={post.slug} className="glass-card p-8 group">
            <Link href={`/posts/${post.slug}`}>
              <div className="flex flex-col gap-4">
                <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-widest text-violet-400">
                  <span className="flex items-center gap-1">
                    <Tag size={12} /> {post.category}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar size={12} /> {post.date}
                  </span>
                </div>
                <h2 className="text-2xl font-bold group-hover:text-violet-400 transition-colors leading-tight">
                  {post.title}
                </h2>
                <p className="text-neutral-400 leading-relaxed max-w-2xl">
                  {post.excerpt}
                </p>
                <div className="pt-4 flex items-center gap-2 text-sm font-semibold text-white group-hover:text-violet-400">
                  더 알아보기 <span className="transform group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            </Link>
          </article>
        ))}
      </div>
    </main>
  );
}
