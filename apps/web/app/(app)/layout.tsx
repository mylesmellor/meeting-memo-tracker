"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  CheckSquare,
  Users,
  Settings,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/meetings", label: "Meetings", icon: FileText },
  { href: "/actions", label: "Actions", icon: CheckSquare },
  { href: "/teams", label: "Teams", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
];

function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await apiFetch("/api/v1/auth/logout", { method: "POST" });
      router.push("/auth/login");
    } catch {
      toast.error("Logout failed");
    }
  };

  return (
    <>
      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}

      <div
        className={cn(
          "fixed left-0 top-0 z-30 flex h-full w-64 flex-col border-r bg-background transition-transform lg:relative lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 items-center border-b px-6">
          <span className="text-lg font-semibold">MeetingMemo</span>
          <button onClick={onClose} className="ml-auto lg:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => {
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t p-4">
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Log out
          </button>
        </div>
      </div>
    </>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center border-b px-6 lg:hidden">
          <button onClick={() => setSidebarOpen(true)} className="mr-4">
            <Menu className="h-5 w-5" />
          </button>
          <span className="text-lg font-semibold">MeetingMemo</span>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
