export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-substrate-950 bg-dark-gradient">
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-grid-pattern bg-grid opacity-50" />

      {/* Centered content */}
      <div className="relative z-10 flex min-h-screen items-center justify-center px-4 py-12">
        {children}
      </div>

      {/* Decorative circuit traces */}
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-trace-500/20 to-transparent" />
      <div className="absolute top-0 right-0 h-full w-px bg-gradient-to-b from-transparent via-trace-500/20 to-transparent" />
    </div>
  );
}
