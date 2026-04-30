"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import LanguageSwitcher from "./LanguageSwitcher";
import { useState } from "react";

export default function Header({ lang }: { lang: string }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="border-b border-gray-100 bg-white relative z-50">
      <div className="max-w-[1280px] mx-auto px-6 h-16 flex items-center justify-between">
        {/* Site Title */}
        <Link href={`/${lang}`} className="font-bold text-lg tracking-tight text-neutral-900 group">
          Wook&apos;s <span className="text-neutral-500 group-hover:text-blue-600 transition-colors">AI and Marketing</span>
        </Link>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8 text-[13px] font-bold text-neutral-500 uppercase tracking-wider">
          <Link href={`/${lang}/category/marketing`} className="hover:text-blue-600 transition-colors">Marketing</Link>
          <Link href={`/${lang}/category/ai-news`} className="hover:text-blue-600 transition-colors">AI News</Link>
          <Link href={`/${lang}/category/ai-learnings`} className="hover:text-blue-600 transition-colors">AI Learnings</Link>
          <Link href={`/${lang}/category/data`} className="hover:text-blue-600 transition-colors">Data</Link>
          <Link href={`/${lang}/category/career`} className="hover:text-blue-600 transition-colors">Career</Link>
          <LanguageSwitcher currentLang={lang} />
        </nav>
        
        {/* Mobile Nav Toggle */}
        <div className="md:hidden flex items-center gap-4">
          <LanguageSwitcher currentLang={lang} />
          <button 
            className="flex items-center text-neutral-600 hover:text-neutral-900 transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle Menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Nav Dropdown */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-16 left-0 w-full bg-white border-b border-gray-100 shadow-lg px-6 py-4 flex flex-col gap-4 text-sm font-bold text-neutral-600 uppercase tracking-wider">
          <Link href={`/${lang}/category/marketing`} onClick={() => setIsMobileMenuOpen(false)} className="hover:text-blue-600 py-2 border-b border-gray-50">Marketing</Link>
          <Link href={`/${lang}/category/ai-news`} onClick={() => setIsMobileMenuOpen(false)} className="hover:text-blue-600 py-2 border-b border-gray-50">AI News</Link>
          <Link href={`/${lang}/category/ai-learnings`} onClick={() => setIsMobileMenuOpen(false)} className="hover:text-blue-600 py-2 border-b border-gray-50">AI Learnings</Link>
          <Link href={`/${lang}/category/data`} onClick={() => setIsMobileMenuOpen(false)} className="hover:text-blue-600 py-2 border-b border-gray-50">Data</Link>
          <Link href={`/${lang}/category/career`} onClick={() => setIsMobileMenuOpen(false)} className="hover:text-blue-600 py-2">Career</Link>
        </div>
      )}
    </header>
  );
}
