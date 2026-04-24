import Link from "next/link";
import { getSortedPostsData } from "@/lib/posts";

export default function Home() {
  const posts = getSortedPostsData().slice(0, 5); // Take only latest 5 for home page

  return (
    <div className="font-sans">
      {/* Category or Page Header */}
      <h1 className="text-3xl font-extrabold text-neutral-900 mb-2">Recent Posts</h1>
      <p className="text-neutral-500 mb-8 border-b border-gray-100 pb-4">
        최근 발행된 글과 인사이트를 확인하세요.
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

      {posts.length === 5 && (
        <div className="mt-10 pt-4">
          <Link href="/posts" className="px-6 py-3 bg-neutral-900 text-white rounded font-medium hover:bg-neutral-800 transition-colors inline-block text-sm shadow-sm ring-1 ring-neutral-900">
            View All Posts
          </Link>
        </div>
      )}
    </div>
  );
}
