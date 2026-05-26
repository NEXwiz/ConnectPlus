import { Link } from "react-router-dom";
import { ArrowRight, Search, FileText, Code2 } from "lucide-react";
import JobMarquee from "@/components/JobMarquee";

export default function HomePage() {
  return (
    <div className="animate-fade-in">
      {/* Hero with marquee background */}
      <section className="relative py-16 sm:py-24 overflow-hidden">
        {/* Marquee behind hero */}
        <div className="absolute inset-0 flex flex-col justify-center opacity-40 pointer-events-none select-none">
          <JobMarquee />
        </div>

        {/* Hero content */}
        <div className="relative text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Find roles that{" "}
            <span className="text-primary">actually match</span> you.
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground backdrop-blur-sm bg-background/70 rounded-lg px-4 py-2 inline-block">
            Connect+ surfaces the right software engineering roles using semantic
            understanding — not keyword matching. Know exactly where you stand
            before you apply.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link
              to="/jobs"
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Browse Jobs
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 rounded-lg border border-border px-6 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-accent"
            >
              Create Profile
            </Link>
          </div>
        </div>
      </section>

      {/* Feature highlights */}
      <section className="grid gap-6 pb-16 sm:grid-cols-3">
        {[
          {
            icon: Search,
            title: "Semantic Search",
            description:
              "Search by what you mean, not what you type. Similar roles surface together regardless of title variations.",
          },
          {
            icon: Code2,
            title: "GitHub Analysis",
            description:
              "Connect your GitHub and see your projects ranked by relevance to the roles you're targeting.",
          },
          {
            icon: FileText,
            title: "Resume Tailoring",
            description:
              "For any role, get specific feedback on what to highlight, what to change, and where gaps exist.",
          },
        ].map((feature) => (
          <div
            key={feature.title}
            className="rounded-xl border border-border bg-card p-6 transition-colors hover:border-primary/30"
          >
            <feature.icon className="h-8 w-8 text-primary" />
            <h3 className="mt-3 text-lg font-semibold text-card-foreground">
              {feature.title}
            </h3>
            <p className="mt-1.5 text-sm text-muted-foreground">
              {feature.description}
            </p>
          </div>
        ))}
      </section>
    </div>
  );
}
