import { getSortedPostsData, getPostData } from "@/lib/posts";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import Link from "next/link";
import { ArrowLeft, Calendar, Tag, ChevronLeft, ChevronRight } from "lucide-react";
import React from "react";

export async function generateStaticParams() {
  const postsKo = getSortedPostsData('ko');
  const postsEn = getSortedPostsData('en');
  return [
    ...postsKo.map((post) => ({ lang: 'ko', slug: post.slug })),
    ...postsEn.map((post) => ({ lang: 'en', slug: post.slug }))
  ];
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ lang: string; slug: string }>;
}) {
  const { lang, slug } = await params;
  const post = getPostData(slug, lang);

  return (
    <article className="font-sans w-full max-w-none">
      <Link
        href={`/${lang}/posts`}
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

      <div className="prose prose-neutral md:prose-lg max-w-full pb-16
        prose-headings:font-bold prose-headings:text-neutral-900 prose-headings:tracking-tight
        prose-h2:mt-12 prose-h2:mb-6 prose-h2:border-b prose-h2:border-gray-200 prose-h2:pb-2 prose-h2:text-2xl
        prose-h3:mt-8 prose-h3:mb-4 prose-h3:text-xl
        prose-p:leading-[1.8] prose-p:text-neutral-700 prose-p:mb-6 prose-p:text-lg
        prose-li:leading-[1.8] prose-li:text-neutral-700 prose-li:text-lg
        prose-blockquote:not-italic prose-blockquote:border-none prose-blockquote:p-0 prose-blockquote:m-0
        prose-a:text-blue-600 hover:prose-a:text-blue-500 prose-a:underline-offset-4
        prose-img:rounded-lg prose-img:shadow-md prose-code:text-violet-600 prose-code:bg-neutral-100 prose-code:px-1 prose-code:rounded">
        <ReactMarkdown
          rehypePlugins={[rehypeRaw]}
          components={{
            blockquote: ({ children, ...props }: any) => {
              // Custom blockquotes (GitHub Alerts)
              const firstChild = React.Children.toArray(children)[0] as any;
              const firstChildContent = firstChild?.props?.children;
              const firstText = Array.isArray(firstChildContent) ? firstChildContent[0] : firstChildContent;
              
              if (typeof firstText === 'string' && firstText.match(/^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]/i)) {
                return <blockquote className="my-6" {...props}>{children}</blockquote>;
              }
              // Fallback
              return <blockquote className="my-6 border-l-4 border-gray-200 pl-4 py-1 italic text-neutral-600 bg-neutral-50/50 rounded-r-lg" {...props}>{children}</blockquote>;
            },
            p: ({ children, ...props }: any) => {
              // Extract alerts inside paragraphs
              const firstChild = React.Children.toArray(children)[0];
              if (typeof firstChild === 'string' && firstChild.match(/^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]/i)) {
                 const match = firstChild.match(/^\[!(.*?)\]/i);
                 const type = match ? match[1].toUpperCase() : 'NOTE';
                 
                 const newChildren = React.Children.map(children, (child, index) => {
                    if (index === 0 && typeof child === 'string') {
                       return child.replace(/^\[!.*?\]/i, '').trimStart();
                    }
                    return child;
                 });
    
                const styles: Record<string, string> = {
                  'NOTE': 'bg-blue-50/80 border-blue-500 text-blue-900',
                  'TIP': 'bg-emerald-50/80 border-emerald-500 text-emerald-900',
                  'WARNING': 'bg-yellow-50/80 border-yellow-500 text-yellow-900',
                  'IMPORTANT': 'bg-purple-50/80 border-purple-500 text-purple-900',
                  'CAUTION': 'bg-red-50/80 border-red-500 text-red-900',
                };
                const icons: Record<string, string> = {
                  'NOTE': 'ℹ️', 'TIP': '✨', 'WARNING': '⚠️', 'IMPORTANT': '🔥', 'CAUTION': '🛑'
                };
    
                 return (
                   <div className={`border-l-4 p-5 rounded-r-lg ${styles[type] || styles['NOTE']} not-prose mb-6 shadow-sm`}>
                      <div className="font-bold flex items-center gap-2 mb-2 text-sm tracking-wide">{icons[type]} {type}</div>
                      <div className="text-[16px] leading-[1.75] opacity-90">{newChildren}</div>
                   </div>
                 );
              }
              return <p {...props}>{children}</p>;
            }
          }}
        >
          {post.content}
        </ReactMarkdown>
      </div>

      {/* Manual Related Posts Section (Only displays if 'related' is specified in frontmatter) */}
      {post.relatedPosts && post.relatedPosts.length > 0 && (
        <section className="mt-16 pt-12 border-t border-neutral-200">
          <h3 className="text-xl font-bold text-neutral-900 mb-6 flex items-center gap-2">
            💡 작성자가 추천하는 관련 글
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {post.relatedPosts.map(rel => (
              <Link key={rel.slug} href={`/${lang}/posts/${rel.slug}`} className="group flex flex-col p-5 bg-neutral-50 rounded-2xl hover:bg-blue-50/50 transition-colors border border-transparent hover:border-blue-100">
                <span className="text-xs font-semibold text-blue-600 mb-2 uppercase tracking-wider">{rel.category}</span>
                <h4 className="text-[15px] font-bold text-neutral-800 group-hover:text-blue-700 transition-colors line-clamp-2 mb-2 leading-snug">
                  {rel.title}
                </h4>
                <span className="mt-auto text-xs font-medium text-neutral-400">{rel.date}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Prev/Next Navigation (Up to 3 older, 3 newer) */}
      <nav className="grid grid-cols-1 sm:grid-cols-2 gap-8 mt-12 pt-8 border-t border-neutral-100">
        <div>
          <h4 className="text-sm font-bold text-neutral-400 mb-4 uppercase tracking-wider flex items-center gap-1">
            <ChevronLeft size={16} /> 이전 글
          </h4>
          <ul className="space-y-3">
            {post.prevPosts && post.prevPosts.length > 0 ? post.prevPosts.map(p => (
              <li key={p.slug}>
                <Link href={`/${lang}/posts/${p.slug}`} className="group flex flex-col border border-neutral-100 p-4 rounded-xl hover:border-blue-500 hover:bg-blue-50/30 transition-all">
                  <span className="text-[14px] font-semibold text-neutral-800 line-clamp-2 group-hover:text-blue-700">{p.title}</span>
                  <span className="text-xs text-neutral-400 mt-1">{p.date}</span>
                </Link>
              </li>
            )) : <li className="text-sm text-neutral-400">이전 글이 없습니다.</li>}
          </ul>
        </div>
        
        <div>
          <h4 className="text-sm font-bold text-neutral-400 mb-4 uppercase tracking-wider flex items-center justify-end gap-1 text-right">
            다음 글 <ChevronRight size={16} />
          </h4>
          <ul className="space-y-3">
             {post.nextPosts && post.nextPosts.length > 0 ? post.nextPosts.map(p => (
              <li key={p.slug}>
                <Link href={`/${lang}/posts/${p.slug}`} className="group flex flex-col border border-neutral-100 p-4 rounded-xl hover:border-blue-500 hover:bg-blue-50/30 transition-all text-right items-end">
                  <span className="text-[14px] font-semibold text-neutral-800 line-clamp-2 group-hover:text-blue-700">{p.title}</span>
                  <span className="text-xs text-neutral-400 mt-1">{p.date}</span>
                </Link>
              </li>
            )) : <li className="text-sm text-neutral-400 text-right">다음 글이 없습니다.</li>}
          </ul>
        </div>
      </nav>
    </article>
  );
}
