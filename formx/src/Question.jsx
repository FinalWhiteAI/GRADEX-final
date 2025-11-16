import React from 'react'
import FormInput from './FormInput';
import RadioInput from './FormRadio';
import CheckboxInput from './FormCheckbox';
import FormTextarea from './FormTextarea'; // Import FormTextarea

const Questioncard = ({ label, description, children }) => { // Destructured props
  return (
    <div className="rounded-xl bg-card-light p-6 shadow-soft dark:bg-card-dark dark:shadow-soft-dark">
      <label className="block font-serif text-xl font-bold text-text-light dark:text-text-dark">
        {label}
      </label>
      {description && (
        <p className="mt-1 text-sm text-subtle-light dark:text-subtle-dark">
          {description}
        </p>
      )}
      <div className="mt-4">{children}</div>
    </div>
  )
}

function QuestionRenderer(props) { 
  return (
    <Questioncard label={props.label} description={props.description}>
      {(() => {
        switch (props.type) {
          case 'text':
            return (
              <FormInput
                id={props.id}
                placeholder="Enter"
                value={props.value} // Pass value
                onChange={props.onChange} // Pass onChange
              />
            );
          case 'textarea': // Fixed: Was rendering FormInput, now renders FormTextarea
            return (
              <FormTextarea
                id={props.id}
                placeholder="Enter"
                rows={5}
                value={props.value} // Pass value
                onChange={props.onChange} // Pass onChange
              />
            );
          case 'radio':
            return (
              <RadioInput
                id={props.id}
                options={props.options}
                value={props.value} // Pass value
                onChange={props.onChange} // Pass onChange
              />
            );
          case 'checkbox':
            return (
              <CheckboxInput
                id={props.id}
                options={props.options}
                value={props.value || {}} // Pass value, default to empty object
                onChange={props.onChange} // Pass onChange
              />
            );
          default:
            return null;
        }
      })()}
    </Questioncard>
  );
}

export default QuestionRenderer