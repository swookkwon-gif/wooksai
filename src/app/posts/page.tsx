import Link from "next/link";
import { getSortedPostsData } from "@/lib/posts";

export default function PostsArchivePage() {
  const posts = getSortedPostsData();

  return (
    <div className="font-sans">
      <h1 className="text-3xl font-extrabold text-neutral-900 mb-2">Archive</h1>
      <p className="text-neutral-500 mb-8 border-b border-gray-100 pb-4">
        과거부터 작성된 모든 아티클을 확인하실 수 있습니다.
      </p>

      {/* Post List */}
      <div className="flex flex-col">
        {posts.map((post) => (
          <article key={post.slug} className="mm-post-item group">
            <h2 className="text-xl md:text-2xl font-bold mb-2">
              <Link href={`/posts/${post.slug}`} className="text-neutral-900 group-hover:text-blue-600 transition-colors">
                {post.title}
              </Link>
            </h2>
            <div className="text-sm text-neutral-500 mb-3 space-x-3">
              <time dateTime={post.date}>{post.date}</time>
              <span>•</span>
              <span className="font-medium text-neutral-600">{post.category || "Insight"}</span>
            </div>
            <p className="text-neutral-600 leading-relaxed text-sm md:text-base mb-3 max-w-3xl">
              {post.excerpt}
            </p>
            <Link 
              href={`/posts/${post.slug}`} 
              className="inline-block text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors"
            >
              Read more &rarr;
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
