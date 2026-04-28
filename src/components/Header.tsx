import Link from "next/link";
import { Menu } from "lucide-react";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Header({ lang }: { lang: string }) {
  return (
    <header className="border-b border-gray-100 bg-white">
      <div className="max-w-[1280px] mx-auto px-6 h-16 flex items-center justify-between">
        {/* Site Title */}
        <Link href={`/${lang}`} className="font-bold text-lg tracking-tight text-neutral-900 group">
          Wook&apos;s <span className="text-neutral-500 group-hover:text-blue-600 transition-colors">AI and Marketing</span>
        </Link>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8 text-[13px] font-bold text-neutral-500 uppercase tracking-wider">
          <Link href={`/${lang}/category/marketing-insights`} className="hover:text-blue-600 transition-colors">Marketing Insights</Link>
          <Link href={`/${lang}/category/ai-news`} className="hover:text-blue-600 transition-colors">AI News</Link>
          <Link href={`/${lang}/category/ai-learnings`} className="hover:text-blue-600 transition-colors">AI Learnings</Link>
          <Link href={`/${lang}/category/career`} className="hover:text-blue-600 transition-colors">Career</Link>
          <LanguageSwitcher currentLang={lang} />
        </nav>
        
        {/* Mobile Nav Toggle (Visual Only for now) */}
        <button className="md:hidden flex items-center gap-2 text-neutral-600 hover:text-neutral-900">
          <LanguageSwitcher currentLang={lang} />
          <Menu size={24} />
        </button>
      </div>
    </header>
  );
}
