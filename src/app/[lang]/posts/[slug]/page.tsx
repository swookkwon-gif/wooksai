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
        className="inline-flex items-center gap-2 text-neutral-500 hover:text-blue-600 mb-4 md:mb-6 transition-colors group text-sm font-medium"
      >
        <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
        목록으로 돌아가기
      </Link>

      <header className="mb-8 md:mb-10">
        <h1 className="text-2xl md:text-4xl font-bold mb-4 md:mb-6 text-neutral-900 tracking-tight leading-[1.3]">
          {post.title}
        </h1>
        <div className="flex items-center gap-4 text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-6 pb-6 border-b border-neutral-100">
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

      {/* Related Posts Section (Up to 7 posts from the same category) */}
      {post.relatedPosts && post.relatedPosts.length > 0 && (
        <section className="mt-16 pt-12 border-t border-neutral-200">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-xl font-bold text-neutral-900 flex items-center gap-2">
              💡 {post.category} 카테고리의 다른 글
            </h3>
            {post.categoryTotalCount && post.categoryTotalCount > 7 && (
              <Link 
                href={`/${lang}/category/${post.category.toLowerCase().replace(/\s+/g, '-')}`}
                className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors"
              >
                전체보기 &rarr;
              </Link>
            )}
          </div>
          <div className="flex flex-col gap-4">
            {post.relatedPosts.map(rel => (
              <Link key={rel.slug} href={`/${lang}/posts/${rel.slug}`} className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:border-blue-200 hover:shadow-sm transition-all gap-4">
                <div className="flex-1">
                  <h4 className="text-[16px] font-bold text-neutral-800 group-hover:text-blue-700 transition-colors line-clamp-1 mb-1">
                    {rel.title}
                  </h4>
                  {rel.excerpt && (
                    <p className="text-sm text-neutral-500 line-clamp-1">
                      {rel.excerpt}
                    </p>
                  )}
                </div>
                <span className="text-xs font-medium text-neutral-400 shrink-0 sm:text-right">{rel.date}</span>
              </Link>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
