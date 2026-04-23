import { getSortedPostsData, getPostData } from "@/lib/posts";
import ReactMarkdown from "react-markdown";
import Link from "next/link";
import { ArrowLeft, Calendar, Tag } from "lucide-react";

export async function generateStaticParams() {
  const posts = getSortedPostsData();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = getPostData(slug);

  return (
    <article className="min-h-screen px-6 pt-24 pb-32 max-w-3xl mx-auto font-sans bg-white">
      <Link
        href="/posts"
        className="inline-flex items-center gap-2 text-neutral-500 hover:text-black mb-12 transition-colors group text-sm font-medium"
      >
        <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
        목록으로 돌아가기
      </Link>

      <header className="mb-12">
        <h1 className="text-3xl md:text-5xl font-extrabold mb-6 text-neutral-900 tracking-tight leading-tight">
          {post.title}
        </h1>
        <div className="flex items-center gap-4 text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-8 border-b border-neutral-100 pb-8">
          <span className="flex items-center gap-1.5">
            <Tag size={14} /> {post.category || "Insight"}
          </span>
          <span className="flex items-center gap-1.5">
            <Calendar size={14} /> {post.date}
          </span>
        </div>
      </header>

      <div className="prose prose-lg prose-neutral md:prose-xl max-w-none prose-headings:font-bold prose-a:text-blue-600 hover:prose-a:text-blue-500 prose-p:leading-relaxed prose-img:rounded-2xl">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}
