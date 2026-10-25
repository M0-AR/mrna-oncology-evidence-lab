(function () {
  "use strict";

  const data = window.EVIDENCE_DATA;
  const claims = data && Array.isArray(data.claims) ? data.claims : [];
  const verdictClass = {
    supported: "verdict--supported",
    partially_supported: "verdict--partially_supported",
    unsupported: "verdict--unsupported",
    not_verifiable: "verdict--not_verifiable"
  };
  const categoryGroup = {
    clinical: "clinical",
    market: "market",
    regulatory: "regulatory",
    financial: "financial",
    valuation: "financial",
    corporate: "other",
    science: "other",
    policy: "other",
    manufacturing: "other",
    publication: "other"
  };

  const claimGrid = document.getElementById("claimGrid");
  const claimCount = document.getElementById("claimCount");
  const searchInput = document.getElementById("claimSearch");
  const filterButtons = Array.from(document.querySelectorAll("[data-filter]"));
  let activeFilter = "all";

  function matchesFilter(claim) {
    if (activeFilter === "all") return true;
    return categoryGroup[claim.category] === activeFilter;
  }

  function matchesQuery(claim, query) {
    if (!query) return true;
    const haystack = [
      claim.id,
      claim.category,
      claim.claim,
      claim.evidence,
      claim.notes,
      claim.verdictLabel
    ].join(" ").toLowerCase();
    return haystack.includes(query);
  }

  function buildClaimCard(claim) {
    const article = document.createElement("article");
    article.className = "claim-card";

    const top = document.createElement("div");
    top.className = "claim-top";

    const id = document.createElement("span");
    id.className = "claim-id";
    id.textContent = claim.id + " · " + claim.category;

    const verdict = document.createElement("span");
    verdict.className = "verdict " + (verdictClass[claim.verdict] || "");
    verdict.textContent = claim.verdictLabel;

    const title = document.createElement("h3");
    title.textContent = claim.claim;

    const evidence = document.createElement("p");
    evidence.className = "claim-evidence";
    evidence.textContent = claim.evidence;

    const meta = document.createElement("p");
    meta.className = "claim-meta";
    meta.textContent = [
      claim.confidence + " confidence",
      claim.sourceCount + (claim.sourceCount === 1 ? " source" : " sources")
    ].join(" · ");

    top.append(id, verdict);
    article.append(top, title, evidence, meta);
    return article;
  }

  function renderClaims() {
    if (!claimGrid) return;
    const query = (searchInput && searchInput.value ? searchInput.value : "").trim().toLowerCase();
    const visible = claims.filter(function (claim) {
      return matchesFilter(claim) && matchesQuery(claim, query);
    });

    claimGrid.replaceChildren();
    if (!visible.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = "No claims match that filter. Try a broader search.";
      claimGrid.append(empty);
    } else {
      visible.forEach(function (claim) {
        claimGrid.append(buildClaimCard(claim));
      });
    }

    if (claimCount) {
      claimCount.textContent = "Showing " + visible.length + " of " + claims.length + " claims";
    }
  }

  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      activeFilter = button.getAttribute("data-filter") || "all";
      filterButtons.forEach(function (other) {
        other.setAttribute("aria-pressed", other === button ? "true" : "false");
      });
      renderClaims();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", renderClaims);
  }

  renderClaims();

  const questions = [
    {
      level: "Foundation",
      prompt: "A hazard ratio of 0.58 means the combination reduced the hazard of recurrence or death by about…",
      options: [
        "58% of patients had no recurrence",
        "42% over the study period",
        "58% in absolute terms",
        "0.58 percentage points"
      ],
      answer: 1,
      why: "The hazard ratio is 0.58, so the relative reduction in the hazard is 1 − 0.58 = 42%. It is not an absolute risk difference and not a cure rate."
    },
    {
      level: "Foundation",
      prompt: "Two-year recurrence-free survival was 82.2% versus 70.0%. What is the absolute gain?",
      options: [
        "12.2 percentage points",
        "42 percentage points",
        "82.2 percentage points",
        "5.8 percentage points"
      ],
      answer: 0,
      why: "82.2 − 70.0 = 12.2 percentage points. That translates to roughly one additional recurrence-free patient for every 8.2 treated."
    },
    {
      level: "Foundation",
      prompt: "Why does the first six months matter in this trial?",
      options: [
        "The benefit is concentrated after month six",
        "The trial failed its primary endpoint",
        "The vaccine was harmful early",
        "The control arm did better throughout"
      ],
      answer: 0,
      why: "The first-six-month RFS hazard ratio was 0.99, essentially flat. The post-six-month hazard ratio was 0.42. The average effect hides a delayed divergence."
    },
    {
      level: "Analyst",
      prompt: "On 22 October 2026, MRNA fell 17.57% close-to-close while the full data were positive. What is the best interpretation?",
      options: [
        "A disclosure and expectations shock",
        "The efficacy data were negative",
        "The trial missed its endpoint",
        "The market proved the vaccine does not work"
      ],
      answer: 0,
      why: "The selloff followed a leak and a later positive full release. Reporting and analyst commentary point to expectations and disclosure, not negative efficacy. Price is not an endpoint."
    },
    {
      level: "Analyst",
      prompt: "Phase 2 showed a 49% RFS reduction; Phase 3 showed 42%. What does the attenuation suggest?",
      options: [
        "The earlier estimate was likely optimistic",
        "The Phase 3 trial was invalid",
        "The vaccine works better in Phase 3",
        "There is no effect at all"
      ],
      answer: 0,
      why: "Effect sizes often shrink when a promising Phase 2 moves to a larger trial. The Phase 3 result remains positive; the attenuation changes the size of the claim, not its direction."
    },
    {
      level: "Analyst",
      prompt: "In this repository, “supported” means…",
      options: [
        "The claim faithfully matches the cited evidence",
        "The claim has been proven true in every context",
        "The source is peer reviewed",
        "The claim has been approved by a regulator"
      ],
      answer: 0,
      why: "The ledger grades fidelity to evidence. A claim that “HHS said X” can be supported even if X is scientifically contested. Supported is not the same as true."
    },
    {
      level: "Professional",
      prompt: "Why use a placebo event study instead of relying only on a normal-theory p-value?",
      options: [
        "It gives empirical inference without assuming normal returns",
        "It proves the event caused the move",
        "It removes every possible confounder",
        "It measures clinical efficacy"
      ],
      answer: 0,
      why: "Placebo inference compares the real event with thousands of pseudo-events. It is robust to non-normality, but it still cannot prove causality or rule out all omitted news."
    },
    {
      level: "Professional",
      prompt: "Which statement is best supported by the evidence?",
      options: [
        "The trial met its RFS and DMFS endpoints",
        "The vaccine is approved for melanoma",
        "The trial proved an overall survival benefit",
        "The October data were negative"
      ],
      answer: 0,
      why: "RFS and DMFS were met. Melanoma approval is absent, OS is immature (HR 0.77, 0.45–1.31, p=.33), and the October full data were positive."
    }
  ];

  const quizForm = document.getElementById("quizForm");
  const quizQuestion = document.getElementById("quizQuestion");
  const quizOptions = document.getElementById("quizOptions");
  const quizFeedback = document.getElementById("quizFeedback");
  const quizSubmit = document.getElementById("quizSubmit");
  const quizNext = document.getElementById("quizNext");
  const quizProgress = document.getElementById("quizProgress");
  const quizLevel = document.getElementById("quizLevel");
  const quizScore = document.getElementById("quizScore");
  const quizScoreValue = document.getElementById("quizScoreValue");
  const quizScoreText = document.getElementById("quizScoreText");
  const quizRestart = document.getElementById("quizRestart");
  let quizIndex = 0;
  let quizScoreCount = 0;
  let quizAnswered = false;

  function renderQuiz() {
    if (!quizForm || !quizQuestion || !quizOptions) return;
    const question = questions[quizIndex];
    quizAnswered = false;
    quizForm.hidden = false;
    quizScore.classList.remove("is-visible");
    quizSubmit.hidden = false;
    quizSubmit.disabled = false;
    quizNext.hidden = true;
    quizFeedback.textContent = "";
    quizProgress.textContent = "Question " + (quizIndex + 1) + " of " + questions.length;
    quizLevel.textContent = question.level;
    quizQuestion.textContent = question.prompt;
    quizOptions.replaceChildren();

    question.options.forEach(function (optionText, optionIndex) {
      const label = document.createElement("label");
      label.className = "option";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = "quiz-option";
      input.value = String(optionIndex);

      const span = document.createElement("span");
      span.textContent = optionText;

      label.append(input, span);
      quizOptions.append(label);
    });
  }

  function markAnswer() {
    if (!quizForm || quizAnswered) return;
    const selected = quizForm.querySelector('input[name="quiz-option"]:checked');
    if (!selected) {
      quizFeedback.textContent = "Choose one answer, then check it.";
      return;
    }

    quizAnswered = true;
    const question = questions[quizIndex];
    const selectedIndex = Number(selected.value);
    const isCorrect = selectedIndex === question.answer;
    if (isCorrect) quizScoreCount += 1;

    Array.from(quizOptions.querySelectorAll("input")).forEach(function (input) {
      input.disabled = true;
      const label = input.closest(".option");
      if (!label) return;
      if (Number(input.value) === question.answer) label.classList.add("is-correct");
      if (Number(input.value) === selectedIndex && !isCorrect) label.classList.add("is-wrong");
    });

    quizFeedback.innerHTML = "";
    const verdict = document.createElement("strong");
    verdict.textContent = isCorrect ? "Correct. " : "Not quite. ";
    const explanation = document.createElement("span");
    explanation.textContent = question.why;
    quizFeedback.append(verdict, explanation);

    quizSubmit.hidden = true;
    quizNext.hidden = false;
    quizNext.textContent = quizIndex === questions.length - 1 ? "See my score" : "Next question";
    quizNext.focus();
  }

  function showQuizScore() {
    quizForm.hidden = true;
    quizScore.classList.add("is-visible");
    quizScoreValue.textContent = quizScoreCount + " / " + questions.length;
    let message = "";
    if (quizScoreCount === questions.length) {
      message = "Professional grade. You can explain the trial, the timing, and the market reaction without confusing price with efficacy.";
    } else if (quizScoreCount >= 6) {
      message = "Analyst grade. You have the core story. Revisit the two attenuation questions to sharpen the edge.";
    } else if (quizScoreCount >= 4) {
      message = "Solid foundation. The primer and the claim ledger will close the gaps quickly.";
    } else {
      message = "Start with the 90-second primer, then try again. The goal is interpretation, not memorization.";
    }
    quizScoreText.textContent = message;
  }

  if (quizForm) {
    quizForm.addEventListener("submit", function (event) {
      event.preventDefault();
      markAnswer();
    });
  }

  if (quizNext) {
    quizNext.addEventListener("click", function () {
      if (!quizAnswered) return;
      if (quizIndex === questions.length - 1) {
        showQuizScore();
      } else {
        quizIndex += 1;
        renderQuiz();
      }
    });
  }

  if (quizRestart) {
    quizRestart.addEventListener("click", function () {
      quizIndex = 0;
      quizScoreCount = 0;
      renderQuiz();
    });
  }

  renderQuiz();

  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
