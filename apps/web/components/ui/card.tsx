import { clsx } from "clsx";
import type { HTMLAttributes } from "react";

const base = "rounded-xl border border-slate-700 bg-slate-900/80 p-6 shadow-lg";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={clsx(base, className)} {...props} />;
}
