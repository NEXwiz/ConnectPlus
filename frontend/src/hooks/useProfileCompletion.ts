import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/services/api";

interface ProfileCompletion {
  isComplete: boolean;
  progress: number;
  missingFields: string[];
  loading: boolean;
}

export function useProfileCompletion(): ProfileCompletion {
  const { user } = useAuth();
  const [state, setState] = useState<ProfileCompletion>({
    isComplete: false,
    progress: 0,
    missingFields: [],
    loading: true,
  });

  useEffect(() => {
    if (!user) {
      setState((s) => ({ ...s, loading: false }));
      return;
    }
    api
      .get("/api/profiles/completion")
      .then((res) => {
        setState({
          isComplete: res.data.is_complete,
          progress: res.data.progress,
          missingFields: res.data.missing_fields,
          loading: false,
        });
      })
      .catch(() => setState((s) => ({ ...s, loading: false })));
  }, [user]);

  return state;
}
