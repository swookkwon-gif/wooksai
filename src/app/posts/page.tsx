import { getSortedPostsData } from "@/lib/posts";
import Link from "next/link";
import { ArrowLeft, Calendar, Tag } from "lucide-react";

export default function PostsPage() {
  const posts = getSortedPostsData();

  return (
    <main className="min-h-screen px-6 pt-24 pb-24 max-w-4xl mx-auto font-sans bg-white">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-neutral-500 hover:text-black mb-12 transition-colors group text-sm font-medium"
      >
        <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
        홈으로 돌아가기
      </Link>

      <header className="mb-16 border-b border-neutral-100 pb-8">
        <h1 className="text-4xl md:text-5xl font-extrabold font-outfit mb-4 text-neutral-900 tracking-tight">AI Insight Reports</h1>
        <p className="text-neutral-500 text-lg">AI가 분석한 최신 트렌드와 인사이트를 확인하세요.</p>
      </header>

      <div className="space-y-6">
        {posts.map((post) => (
          <article key={post.slug} className="clean-card p-8 group">
            <Link href={`/posts/${post.slug}`}>
              <div className="flex flex-col gap-4">
                <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-widest text-blue-600">
                  <span className="flex items-center gap-1.5">
                    <Tag size={12} /> {post.category || "Insight"}
                  </span>
                  <span className="flex items-center gap-1.5 text-neutral-400 font-medium">
                    <Calendar size={12} /> {post.date}
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-neutral-900 group-hover:text-blue-600 transition-colors leading-tight">
                  {post.title}
                </h2>
                <p className="text-neutral-500 leading-relaxed text-base">
                  {post.excerpt}
                </p>
                <div className="pt-2 flex items-center gap-2 text-sm font-semibold text-neutral-900 group-hover:text-blue-600">
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
