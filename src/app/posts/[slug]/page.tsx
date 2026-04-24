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
    <article className="font-sans w-full max-w-none">
      <Link
        href="/posts"
        className="inline-flex items-center gap-2 text-neutral-500 hover:text-blue-600 mb-8 transition-colors group text-sm font-medium"
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

      <div className="prose prose-neutral md:prose-lg max-w-full pb-20
        prose-headings:font-bold prose-headings:text-neutral-900 prose-headings:tracking-tight
        prose-h2:mt-12 prose-h2:mb-6 prose-h2:border-b prose-h2:border-gray-200 prose-h2:pb-2 prose-h2:text-2xl
        prose-h3:mt-8 prose-h3:mb-4 prose-h3:text-xl
        prose-p:leading-[1.8] prose-p:text-neutral-700 prose-p:mb-6 prose-p:text-lg
        prose-li:leading-[1.8] prose-li:text-neutral-700 prose-li:text-lg
        prose-blockquote:border-l-4 prose-blockquote:border-gray-200 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-neutral-600
        prose-a:text-blue-600 hover:prose-a:text-blue-500 prose-a:underline-offset-4
        prose-img:rounded-lg prose-img:shadow-md prose-code:text-violet-600 prose-code:bg-neutral-100 prose-code:px-1 prose-code:rounded">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}
