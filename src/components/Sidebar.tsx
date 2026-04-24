import { MapPin, Link as LinkIcon } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-full md:w-[280px] shrink-0 mb-10 md:mb-0">
      <div className="md:sticky md:top-24 flex flex-col md:block items-center md:items-start text-center md:text-left">
        {/* Avatar Placeholder */}
        <div className="w-28 h-28 md:w-32 md:h-32 rounded-full bg-neutral-200 overflow-hidden mb-4 border border-neutral-200 shadow-sm relative shrink-0">
          {/* As requested, a clean placeholder. The user can swap this out easily. */}
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
        <ul className="text-sm text-neutral-600 space-y-3 w-full max-w-[200px]">
          <li className="flex justify-center md:justify-start items-center gap-3">
            <MapPin size={16} className="text-neutral-400" /> Seoul, KR
          </li>
          <li className="flex justify-center md:justify-start items-center gap-3">
            <LinkIcon size={16} className="text-neutral-400" />
            <a href="https://www.linkedin.com/in/wook-kwon/" target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 hover:underline">LinkedIn</a>
          </li>
        </ul>
      </div>
    </aside>
  );
}
