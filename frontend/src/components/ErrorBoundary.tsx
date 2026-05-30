import React from "react";

interface State {
  error: Error | null;
}

interface Props {
  children: React.ReactNode;
  fallback?: (error: Error, reset: () => void) => React.ReactNode;
}

/**
 * App-root error boundary. Catches render errors, displays a non-removable
 * disclaimer-respecting fallback, and forwards to Sentry if the SDK is
 * present. Sentry is loaded dynamically so missing it doesn't fail the build.
 */
export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    try {
      // Best-effort Sentry capture; no hard dependency.
      const w = window as unknown as { Sentry?: { captureException: (e: unknown, x?: unknown) => void } };
      if (w.Sentry?.captureException) {
        w.Sentry.captureException(error, { extra: { componentStack: info.componentStack } });
      }
    } catch {
      /* swallow — error UI is the priority */
    }
    // Surface in dev console either way.
    // eslint-disable-next-line no-console
    console.error("ErrorBoundary caught:", error, info);
  }

  reset = (): void => this.setState({ error: null });

  render(): React.ReactNode {
    if (this.state.error) {
      if (this.props.fallback) return this.props.fallback(this.state.error, this.reset);
      return (
        <div role="alert" style={{ padding: 24, maxWidth: 720, margin: "40px auto", fontFamily: "system-ui" }}>
          <h1 style={{ fontSize: 20, marginBottom: 8 }}>Something went wrong.</h1>
          <p style={{ color: "#555", marginBottom: 16 }}>
            The page failed to render. Reloading often clears transient issues. If it persists,
            contact your administrator.
          </p>
          <details style={{ marginBottom: 16 }}>
            <summary>Technical details</summary>
            <pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>{this.state.error.message}</pre>
          </details>
          <button
            onClick={this.reset}
            style={{ padding: "8px 16px", border: "1px solid #ddd", borderRadius: 6, cursor: "pointer" }}
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
