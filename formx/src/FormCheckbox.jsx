function CheckboxOption({ label, name, value, checked, onChange }) {
  return (
    <label className="flex cursor-pointer items-center gap-4 rounded-lg border border-border-light p-4 transition-colors has-[:checked]:border-accent has-[:checked]:bg-primary/10 dark:border-border-dark dark:has-[:checked]:border-accent">
      <div className="relative flex size-6 items-center justify-center rounded-lg border-2 border-border-light bg-background-light transition-colors dark:border-border-dark dark:bg-background-dark checkbox-custom">
        {checked && (
          <span className="material-symbols-outlined text-sm text-white">
            check
          </span>
        )}
        <input
          className="absolute size-full cursor-pointer appearance-none"
          name={name}
          type="checkbox"
          value={value}
          checked={checked}
          onChange={onChange}
        />
      </div>
      <span className="text-base text-text-light dark:text-text-dark">{label}</span>
    </label>
  );
}
function CheckboxInput({ id, options, value, onChange }) {
  return (
    <div className="space-y-3">
      {options.map((option) => (
        <CheckboxOption
          key={option.value}
          label={option.label}
          name={id} // The question ID
          value={option.value} // The specific option value
          checked={value[option.value]} // Checked state from the { social: true, ... } object
          onChange={onChange}
        />
      ))}
    </div>
  );
}

export default CheckboxInput