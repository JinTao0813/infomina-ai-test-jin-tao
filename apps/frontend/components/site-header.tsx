import Link from "next/link";

export default function SiteHeader({ active }: { active: "analysis" | "prototype" }) {
  return (
    <header className="site-header">
      <Link className="brand-lockup" href="/" aria-label="From Data to Product home">
        <span className="brand-mark" aria-hidden="true">D→P</span>
        <span>From Data to Product</span>
      </Link>
      <nav aria-label="Primary navigation">
        <Link aria-current={active === "analysis" ? "page" : undefined} href="/">
          Analysis
        </Link>
        <Link aria-current={active === "prototype" ? "page" : undefined} href="/prototype/discovery">
          Discovery Mode
        </Link>
      </nav>
    </header>
  );
}
