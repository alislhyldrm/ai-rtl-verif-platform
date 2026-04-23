import { Link, useLocation } from "react-router-dom";
import { Cpu, Play, LayoutDashboard } from "lucide-react";

const NAV = [
  { to: "/", label: "Setup", Icon: LayoutDashboard },
  { to: "/run", label: "Run", Icon: Play },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  return (
    <div className="flex h-screen bg-[hsl(var(--background))]">
      <aside className="w-52 flex-shrink-0 border-r border-[hsl(var(--border))] flex flex-col">
        <div className="p-4 border-b border-[hsl(var(--border))] flex items-center gap-2">
          <Cpu className="h-5 w-5" />
          <span className="text-sm font-semibold tracking-tight">RTL Verif</span>
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {NAV.map(({ to, label, Icon }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors
                ${pathname === to
                  ? "bg-[hsl(var(--muted))] text-[hsl(var(--foreground))]"
                  : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]"
                }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-[hsl(var(--border))]">
          <p className="text-xs text-[hsl(var(--muted-foreground))]">AI-RTL v0.1</p>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}
