import { MapPin, Link as LinkIcon } from "lucide-react";
import { getSortedPostsData } from "@/lib/posts";
import Link from "next/link";

export default function Sidebar() {
  const posts = getSortedPostsData();
  
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
    <aside className="w-full md:w-[280px] shrink-0 mb-10 md:mb-0">
      <div className="md:sticky md:top-24 md:max-h-[calc(100vh-8rem)] md:overflow-y-auto no-scrollbar flex flex-col md:block items-center md:items-start text-center md:text-left pt-2">

        {/* Category Navigation (Minimal Mistakes & WikiDocs Style) */}
        <div className="w-full text-left pt-8 border-t border-gray-200 hidden md:block">
          <h3 className="font-bold text-neutral-900 mb-6 uppercase tracking-widest text-xs">Categories</h3>
          <nav className="space-y-4">
            {Object.entries(categories).map(([category, catPosts]) => {
              const displayPosts = catPosts.slice(0, 5);
              const hasMore = catPosts.length > 5;
              const catSlug = category.toLowerCase().replace(/\s+/g, '-');

              return (
                <details key={category} className="group" open>
                  <summary className="font-semibold text-neutral-800 mb-2 text-sm cursor-pointer list-none flex items-center justify-between hover:text-blue-600 transition-colors outline-none select-none">
                    {category}
                    <span className="text-neutral-400 text-xs transition-transform duration-200 group-open:rotate-180">▼</span>
                  </summary>
                  <ul className="space-y-2 border-l-[3px] border-gray-100 pl-4 mb-2 mt-2">
                    {displayPosts.map(post => (
                      <li key={post.slug}>
                        <Link 
                          href={`/posts/${post.slug}`}
                          className="text-sm text-neutral-500 hover:text-blue-600 transition-colors line-clamp-2 leading-relaxed"
                          title={post.title}
                        >
                          {post.title}
                        </Link>
                      </li>
                    ))}
                    {hasMore && (
                      <li className="pt-2">
                        <Link 
                          href={`/category/${catSlug}`} 
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
