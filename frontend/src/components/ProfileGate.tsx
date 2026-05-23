import { useEffect, useState, type ReactNode } from "react";
import { Navigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/services/api";
import { Loader2, UserCircle } from "lucide-react";

export default function ProfileGate({ children }: { children: ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const [checking, setChecking] = useState(true);
  const [complete, setComplete] = useState(false);

  useEffect(() => {
    if (authLoading || !user) return;

    api
      .get("/api/profiles/completion")
      .then((res) => setComplete(res.data.is_complete))
      .catch(() => setComplete(false))
      .finally(() => setChecking(false));
  }, [user, authLoading]);

  if (authLoading || checking) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (!complete) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
        <UserCircle className="h-12 w-12 text-muted-foreground/50" />
        <h2 className="mt-4 text-lg font-semibold text-foreground">
          Set up your profile first
        </h2>
        <p className="mt-1 text-sm text-muted-foreground max-w-sm">
          We need your skills, target roles, and experience to generate personalized recommendations.
        </p>
        <Link
          to="/profile"
          className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Complete Profile
        </Link>
      </div>
    );
  }

  return <>{children}</>;
}
