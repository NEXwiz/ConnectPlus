import { type ReactNode } from "react";
import { Link } from "react-router-dom";
import { type LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: { label: string; to?: string; onClick?: () => void };
  children?: ReactNode;
}

export default function EmptyState({ icon: Icon, title, description, action, children }: EmptyStateProps) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-card/50 p-12 text-center">
      <Icon className="mx-auto h-10 w-10 text-muted-foreground/50" />
      <h3 className="mt-3 text-sm font-semibold text-foreground">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground max-w-sm mx-auto">{description}</p>
      {action && (
        action.to ? (
          <Link
            to={action.to}
            className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            {action.label}
          </Link>
        ) : (
          <button
            onClick={action.onClick}
            className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            {action.label}
          </button>
        )
      )}
      {children}
    </div>
  );
}
