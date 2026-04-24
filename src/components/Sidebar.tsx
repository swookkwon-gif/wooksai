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
      <div className="md:sticky md:top-24 flex flex-col md:block items-center md:items-start text-center md:text-left">
        
        {/* Profile Section */}
        <div className="w-28 h-28 md:w-32 md:h-32 rounded-full bg-neutral-200 overflow-hidden mb-4 border border-neutral-200 shadow-sm relative shrink-0">
          <div className="absolute inset-0 flex items-center justify-center text-4xl">
            💻
          </div>
        </div>

        <h2 className="text-xl font-bold text-neutral-900 mb-1">Wook</h2>
        <p className="text-neutral-500 text-sm mb-4">Marketer & AI Enthusiast</p>

        <p className="text-sm text-neutral-600 mb-6 max-w-xs leading-relaxed">
          Digital Marketing and Ecommerce expert. Ph.D candidate Data science and AI
        </p>

        {/* Info & Social Links */}
        <ul className="text-sm text-neutral-600 space-y-3 w-full max-w-[200px] mb-12">
          <li className="flex justify-center md:justify-start items-center gap-3">
            <MapPin size={16} className="text-neutral-400" /> Seoul, KR
          </li>
          <li className="flex justify-center md:justify-start items-center gap-3">
            <LinkIcon size={16} className="text-neutral-400" />
            <a href="https://www.linkedin.com/in/wook-kwon/" target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 hover:underline">LinkedIn</a>
          </li>
        </ul>

        {/* Category Navigation (Minimal Mistakes Style) */}
        <div className="w-full text-left pt-8 border-t border-gray-200 hidden md:block">
          <h3 className="font-bold text-neutral-900 mb-6 uppercase tracking-widest text-xs">Categories</h3>
          <nav className="space-y-8">
            {Object.entries(categories).map(([category, catPosts]) => (
              <div key={category}>
                <h4 className="font-semibold text-neutral-800 mb-3 text-sm">{category}</h4>
                <ul className="space-y-2 border-l-[3px] border-gray-100 pl-4">
                  {catPosts.map(post => (
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
                </ul>
              </div>
            ))}
          </nav>
        </div>

      </div>
    </aside>
  );
}
