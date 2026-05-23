import { Link } from "react-router-dom";
import { AlertCircle } from "lucide-react";

export default function ProfileGateBanner({ message }: { message?: string }) {
  return (
    <div className="rounded-xl border border-amber-300 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 p-4 flex items-start gap-3">
      <AlertCircle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
      <div>
        <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
          {message || "Complete your profile to unlock this feature"}
        </p>
        <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
          Add your skills, target roles, and experience to get personalized insights.
        </p>
        <Link
          to="/profile"
          className="inline-block mt-2 text-xs font-semibold text-primary hover:underline"
        >
          Complete Profile →
        </Link>
      </div>
    </div>
  );
}
