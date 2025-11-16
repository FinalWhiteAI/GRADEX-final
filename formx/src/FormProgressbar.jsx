function ProgressBar({ completed, total }) {
  const percent = total > 0 ? (completed / total) * 100 : 0;

  return (
    <footer className="fixed bottom-0 left-0 right-0 z-10 bg-background-light/80 pb-4 pt-3 backdrop-blur-sm dark:bg-background-dark/80">
      <div className="mx-auto w-full max-w-2xl px-4">
        <div className="w-full rounded-full bg-border-light dark:bg-border-dark">
          <div
            // UPDATED THIS LINE: Removed gradient, now solid accent color
            className="h-2 rounded-full bg-accent"
            style={{ width: `${percent}%` }}
          ></div>
        </div>
        <p className="mt-2 text-center text-sm font-medium text-subtle-light dark:text-subtle-dark">
          {completed} of {total} questions completed
        </p>
      </div>
    </footer>
  );
}

export default ProgressBar