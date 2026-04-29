import { MapPin, Link as LinkIcon, ChevronDown } from "lucide-react";
import { getSortedPostsData } from "@/lib/posts";
import Link from "next/link";

export default function Sidebar({ lang }: { lang: string }) {
  const posts = getSortedPostsData(lang);
  
  // 포스트들을 카테고리별로 그룹핑
  const categories = posts.reduce((acc, post) => {
    const cat = post.category || "Insight";
    if (!acc[cat]) {
      acc[cat] = [];
    }
    acc[cat].push(post);
    return acc;
  }, {} as Record<string, typeof posts>);

  return (
    <aside className="hidden md:block w-[280px] shrink-0">
      <div className="md:sticky md:top-6 md:max-h-[calc(100vh-3rem)] md:overflow-y-auto no-scrollbar flex flex-col md:block items-center md:items-start text-center md:text-left pt-2">

        {/* Category Navigation (Minimal Mistakes & WikiDocs Style) */}
        <div className="w-full text-left pt-2 hidden md:block">
          <nav className="space-y-6">
            {Object.entries(categories).map(([category, catPosts]) => {
              const displayPosts = catPosts.slice(0, 5);
              const hasMore = catPosts.length > 5;
              const catSlug = category.toLowerCase().replace(/\s+/g, '-');

              return (
                <details key={category} className="group" open>
                  <summary className="font-bold text-neutral-800 mb-3 text-base cursor-pointer list-none flex items-center justify-between hover:text-blue-600 transition-colors outline-none select-none">
                    {category}
                    <ChevronDown className="w-4 h-4 text-neutral-400 transition-transform duration-200 group-open:rotate-180" />
                  </summary>
                  <ul className="space-y-3 pl-2 mb-2 mt-1">
                    {displayPosts.map(post => (
                      <li key={post.slug}>
                        <Link 
                          href={`/${lang}/posts/${post.slug}`}
                          className="text-sm text-neutral-600 hover:text-blue-600 transition-colors line-clamp-2 leading-relaxed"
                          title={post.title}
                        >
                          {post.title}
                        </Link>
                      </li>
                    ))}
                    {hasMore && (
                      <li className="pt-2">
                        <Link 
                          href={`/${lang}/category/${catSlug}`} 
                          className="text-xs font-bold text-blue-500 hover:text-blue-700 flex items-center gap-1"
                        >
                          + 전체 보기 ({catPosts.length})
                        </Link>
                      </li>
                    )}
                  </ul>
                </details>
              );
            })}
          </nav>
        </div>

      </div>
    </aside>
  );
}
