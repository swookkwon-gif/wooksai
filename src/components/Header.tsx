import Link from "next/link";
import { Menu } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-gray-100 bg-white">
      <div className="max-w-[1280px] mx-auto px-6 h-16 flex items-center justify-between">
        {/* Site Title */}
        <Link href="/" className="font-bold text-lg tracking-tight text-neutral-900 group">
          Wook&apos;s <span className="text-neutral-500 group-hover:text-blue-600 transition-colors">AI and Marketing</span>
        </Link>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-neutral-600">
          <Link href="/" className="hover:text-neutral-900 transition-colors">About</Link>
          <Link href="/posts" className="hover:text-neutral-900 transition-colors">Posts</Link>
          <Link href="/posts" className="hover:text-neutral-900 transition-colors">Categories</Link>
        </nav>
        
        {/* Mobile Nav Toggle (Visual Only for now) */}
        <button className="md:hidden text-neutral-600 hover:text-neutral-900">
          <Menu size={24} />
        </button>
      </div>
    </header>
  );
}
