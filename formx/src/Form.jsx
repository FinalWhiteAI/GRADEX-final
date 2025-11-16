import React, { useState, useEffect } from "react"; // Import useEffect
import FormHeader from "./FormHeader";
import QuestionRenderer from "./Question";
import FormProgressbar from "./FormProgressbar";
import { useParams } from "react-router-dom";
import {Mosaic}  from 'react-loading-indicators'

const Form = () => {
  const { item } = useParams(); // Gets the form ID from the URL

  const [formConfig, setFormConfig] = useState(null);

  const [formData, setFormData] = useState({});

  useEffect(() => {
    console.log("Effect is running."); // <-- ADD THIS
    
    if (!item) {
      console.log("Failed check: 'item' is undefined or empty."); // <-- ADD THIS
      return;
    }

    const fetchFormConfig = async () => {
      console.log("fetchFormConfig is being called with item:", item); // <-- ADD THIS
      
      // Use the dynamic 'item' from the URL, not a hardcoded ID
      const url = `http://localhost:8002/form/${item}`;
      
      try {
        console.log("Attempting to fetch:", url); // You had this, it's good
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(
            `Network response was not ok: ${response.statusText}`
          );
        }
        const data = await response.json(); // 'data' is our 'js' object

        // 1. Store the fetched form configuration
        setFormConfig(data);

        // 2. Initialize the formData state *after* data is fetched
        const initialState = {};
        data.questions.forEach((q) => {
          if (q.type === "checkbox") {
            initialState[q.questionId] = {};
          } else {
            initialState[q.questionId] = "";
          }
        });
        setFormData(initialState);
      } catch (error) {
        console.error("Failed to fetch form configuration:", error);
        // You could set an error state here to show a message to the user
      }
    };

    fetchFormConfig();
  }, [item]); // Re-run this effect if 'item' changes

  // Handle input changes (this logic was correct)
  const handleInputChange = (id, type, e) => {
    const { value, checked } = e.target;

    setFormData((prevData) => {
      if (type === "checkbox") {
        return {
          ...prevData,
          [id]: {
            ...prevData[id],
            [value]: checked,
          },
        };
      }
      return {
        ...prevData,
        [id]: value,
      };
    });
  };

  // Show a loading state while fetching data
  if (!formConfig) {
    return (
      <div className="flex min-h-screen w-full items-center justify-center bg-background-light dark:bg-background-dark">
        <p className="text-text-light dark:text-text-dark">
            <Mosaic color="gray" size="medium" text="" textColor="" />
        </p>
      </div>
    );
  }

  // --- Calculations ---
  // These now run only *after* formConfig is loaded
  const totalQuestions = formConfig.questions.length;
  const completedCount = formConfig.questions.reduce((count, q) => {
    const value = formData[q.questionId];
    if (q.type === "checkbox") {
      if (value && Object.values(value).some((v) => v === true)) {
        return count + 1;
      }
    } else {
      if (value) {
        return count + 1;
      }
    }
    return count;
  }, 0);

  // console.log("Form Config:", formConfig);
  // console.log("Form Data:", formData);

  return (
    <div className="relative flex min-h-screen w-full flex-col bg-background-light dark:bg-background-dark">
      {/* Use the fetched title */}
      <FormHeader title={formConfig.title} />

      <main className="flex-1 w-full max-w-2xl mx-auto px-4 pb-28 pt-6">
        <h2 className="font-serif text-[32px] font-bold leading-tight tracking-tight text-text-light dark:text-text-dark">
          Share Your Experience
        </h2>
        {/* Use the fetched description */}
        <p className="mt-2 text-base font-normal leading-normal text-subtle-light dark:text-subtle-dark">
          {formConfig.description}
        </p>

        <form className="mt-8 space-y-8">
          {/* Map over the fetched questions */}
          {formConfig.questions.map((question) => (
            <QuestionRenderer
              key={question.questionId}
              label={question.label}
              description={question.description}
              id={question.questionId}
              options={question.options}
              type={question.type}
              value={formData[question.questionId]}
              onChange={(e) =>
                handleInputChange(question.questionId, question.type, e)
              }
            />
          ))}

          <button
            type="submit"
            className="!mt-10 w-full rounded-lg bg-accent p-4 text-lg font-bold text-text-light transition-colors hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent/50 dark:text-text-dark"
          >
            Submit Feedback
          </button>
        </form>
      </main>

      <FormProgressbar completed={completedCount} total={totalQuestions} />
    </div>
  );
};

export default Form;
