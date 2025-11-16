export function RadioOption({ label, name, value, checked, onChange }) {
  return (
    <label className="flex cursor-pointer items-center gap-4 rounded-lg border border-border-light p-4 transition-colors has-[:checked]:border-accent has-[:checked]:bg-primary/10 dark:border-border-dark dark:has-[:checked]:border-accent">
      <div className="relative flex size-6 items-center justify-center rounded-full border-2 border-border-light bg-background-light dark:border-border-dark dark:bg-background-dark">
        <input
          className="radio-custom absolute size-full cursor-pointer appearance-none rounded-full"
          name={name}
          type="radio"
          value={value}
          checked={checked}
          onChange={onChange}
        />
      </div>
      <span className="text-base text-text-light dark:text-text-dark">{label}</span>
    </label>
  );
}

function RadioInput({ id, options, value, onChange }) {
  return (
    <div className="space-y-3">
      {options.map((option) => (
        <RadioOption
          key={option.value}
          label={option.label}
          name={id}
          value={option.value}
          checked={value === option.value}
          onChange={onChange}
        />
      ))}
    </div>
  );
}

export default RadioInput