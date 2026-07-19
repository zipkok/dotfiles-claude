export const meta = {
  name: 'ship-discussion-panel',
  description: 'ship-discussion의 Plan→Review→Result를 한 번에 체이닝 — 기법 병렬 실행, Review 재작업 루프, Result 라운드 반복까지 사람 개입 없이 진행',
  phases: [
    { title: 'Plan', detail: 'mece/first-principles/pre-mortem/inversion 4기법 병렬 → synthesizer 종합 (+대안·평가기준)' },
    { title: 'Review', detail: 'steel-man 정성 검증 + synthesizer 정량 루브릭 채점 → 하이브리드 판정, fail시 Plan 재작업(최대 2회)' },
    { title: 'Result', detail: '쟁점별 position A/B → synthesizer 라운드 판정, 전부 해결되거나 최대 5라운드까지 자동 반복' },
  ],
}

// args (호출자가 매번 넘김):
//   { stage: 'pipeline', issues, context, slug? }               — Plan→Review→Result 전체 체이닝 (기본, 권장)
//   { stage: 'plan', issues, context, slug? }                   — Plan 한 단계만 (디버깅용)
//   { stage: 'review', plan, context, slug? }                   — Review 한 단계만 (디버깅용)
//   { stage: 'result', issues: [{issue, history}], context, slug? } — Result 한 라운드만 (디버깅용)
// slug: 호출한 RFC 폴더명(예: '0003-improve-work-quality-v2') — 있으면 라벨/로그에 붙여 /workflows
// 화면에서 여러 ship-discussion 실행을 구분할 수 있게 한다. meta.name은 스크립트 고정 literal이라
// 실행마다 못 바꾸므로, 최상위 실행 이름 자체에는 못 붙는다 — 실행 시작 직후 log()로 가장 먼저
// 찍어서 실행 내부(진행 상황 화면)에서는 바로 보이게 한다.
//
// pipeline 스테이지가 왜 필요한가: Spec/Clarify는 사용자와의 실시간 대화가 필요해 워크플로로 못 옮기지만,
// Plan→Review(fail시 재작업 루프)→Result(라운드 반복)는 "다음에 뭘 할지"가 전부 정해진 규칙(게이트
// 통과/조건부/fail, 3회 초과 시 에스컬레이션, 전부 해결되거나 5라운드)으로 결정되고 사람이 매번
// 개입할 필요가 없다 — 그래서 하나의 워크플로 호출로 체이닝한다. 유일한 예외(3회 초과 fail)만
// status: 'escalation_needed'로 조기 반환해 Main이 사용자에게 묻게 한다.

const parsedArgs = typeof args === 'string' ? JSON.parse(args) : args

if (!parsedArgs || !parsedArgs.stage) {
  throw new Error('args.stage가 필요합니다 (pipeline | plan | review | result)')
}

const prefix = parsedArgs.slug ? `${parsedArgs.slug}:` : ''
log(`RFC: ${parsedArgs.slug || '(slug 없음)'}`)

async function runPlan(issues, context, roundNote) {
  phase('Plan')
  const techniques = ['mece', 'first-principles', 'pre-mortem', 'inversion']
  log(`${prefix}Plan${roundNote || ''}: ${techniques.join(', ')} 4개 기법 병렬 적용`)
  const findings = await parallel(
    techniques.map(t => () =>
      agent(
        `기법: ${t}\n대상(구조화된 쟁점 목록): ${JSON.stringify(issues)}\n맥락: ${context}`,
        { agentType: 'ship-discussion-technique-agent', label: `${prefix}plan${roundNote || ''}:${t}`, phase: 'Plan' }
      )
    )
  )
  const synthesis = await agent(
    `모드: plan-종합\n입력 결과들: ${JSON.stringify(findings.filter(Boolean))}\n맥락: ${context}`,
    { agentType: 'ship-discussion-synthesizer', label: `${prefix}plan${roundNote || ''}:synthesize`, phase: 'Plan' }
  )
  return { findings: findings.filter(Boolean), synthesis }
}

async function runReview(planText, context, roundNote) {
  phase('Review')
  const techniques = ['steel-man']
  log(`${prefix}Review${roundNote || ''}: ${techniques.join(', ')} 정성 검증 + synthesizer 정량 루브릭 채점`)
  const findings = await parallel(
    techniques.map(t => () =>
      agent(
        `기법: ${t}\n대상(계획): ${planText}\n맥락: ${context}`,
        { agentType: 'ship-discussion-technique-agent', label: `${prefix}review${roundNote || ''}:${t}`, phase: 'Review' }
      )
    )
  )
  const verdict = await agent(
    `모드: review-판정\n대상(계획, 대안·평가기준 포함): ${planText}\n입력 결과들: ${JSON.stringify(findings.filter(Boolean))}\n맥락: ${context}`,
    { agentType: 'ship-discussion-synthesizer', label: `${prefix}review${roundNote || ''}:verdict`, phase: 'Review' }
  )
  return { findings: findings.filter(Boolean), verdict }
}

function parseReviewBand(verdictText) {
  const m = /결과\s*[:：]\s*(통과|조건부\s*통과|fail)/i.exec(verdictText || '')
  if (!m) return 'unknown'
  const raw = m[1].replace(/\s+/g, '')
  if (raw === '통과') return 'pass'
  if (raw === '조건부통과') return 'conditional'
  return 'fail'
}

async function runResultRound(unresolvedIssues, context, roundNum) {
  phase('Result')
  log(`${prefix}Result ${roundNum}라운드: 쟁점 ${unresolvedIssues.length}개, 쟁점당 position A/B → synthesizer 판정`)
  // issue: { issue, history, alternativeA?, alternativeB? }
  const roundResults = await pipeline(
    unresolvedIssues,
    issue =>
      parallel([
        () =>
          agent(
            `쟁점: ${issue.issue}\n입장: A${issue.alternativeA ? ` (대안: ${issue.alternativeA})` : ''}\n맥락: ${issue.history || context}`,
            { agentType: 'ship-discussion-position', label: `${prefix}result:r${roundNum}:${issue.issue}:A`, phase: 'Result' }
          ),
        () =>
          agent(
            `쟁점: ${issue.issue}\n입장: B${issue.alternativeB ? ` (대안: ${issue.alternativeB})` : ''}\n맥락: ${issue.history || context}`,
            { agentType: 'ship-discussion-position', label: `${prefix}result:r${roundNum}:${issue.issue}:B`, phase: 'Result' }
          ),
      ]),
    (positions, issue) =>
      agent(
        `모드: result-라운드판정\n쟁점: ${issue.issue}\n입력 결과들: ${JSON.stringify((positions || []).filter(Boolean))}\n맥락: ${context}`,
        { agentType: 'ship-discussion-synthesizer', label: `${prefix}result:r${roundNum}:${issue.issue}:synthesize`, phase: 'Result' }
      )
  )
  return roundResults.filter(Boolean)
}

if (parsedArgs.stage === 'plan') {
  const planData = await runPlan(parsedArgs.issues, parsedArgs.context, '')
  return { stage: 'plan', ...planData }
}

if (parsedArgs.stage === 'review') {
  const reviewData = await runReview(parsedArgs.plan, parsedArgs.context, '')
  return { stage: 'review', ...reviewData }
}

if (parsedArgs.stage === 'result') {
  const roundResults = await runResultRound(parsedArgs.issues, parsedArgs.context, 1)
  return { stage: 'result', roundResults }
}

if (parsedArgs.stage === 'pipeline') {
  const MAX_REVIEW_RETRIES = 2 // 총 3회 시도(최초 1 + 재작업 2) 후에도 fail이면 에스컬레이션
  const MAX_RESULT_ROUNDS = 5

  let planData = await runPlan(parsedArgs.issues, parsedArgs.context, '')
  let reviewAttempt = 0
  let reviewData

  while (true) {
    reviewData = await runReview(planData.synthesis, parsedArgs.context, reviewAttempt > 0 ? ` (재작업 ${reviewAttempt}회차 후)` : '')
    const band = parseReviewBand(reviewData.verdict)
    if (band === 'pass' || band === 'conditional') break
    reviewAttempt++
    if (reviewAttempt > MAX_REVIEW_RETRIES) {
      log(`${prefix}Review 같은 게이트 ${reviewAttempt}회째 fail — 에스컬레이션 필요, Main에게 반환`)
      return {
        stage: 'pipeline',
        status: 'escalation_needed',
        plan: planData,
        review: reviewData,
        reviewAttempts: reviewAttempt,
      }
    }
    log(`${prefix}Review fail(${reviewAttempt}회째) — Plan 재작업`)
    planData = await runPlan(
      parsedArgs.issues,
      `${parsedArgs.context}\n\n[Review ${reviewAttempt}회차 fail 사유 — 이번 재작업에 반영할 것]\n${reviewData.verdict}`,
      ` r${reviewAttempt + 1}`
    )
  }

  // Result: 대안이 있는 쟁점만 position A/B 논쟁 대상. plan 전체 맥락은 각 position에게 함께 전달해
  // 대안 텍스트를 스스로 찾아 쓰게 한다 (구조화 추출 없이).
  let unresolved = parsedArgs.issues.map(issueText => ({
    issue: issueText,
    history: `${parsedArgs.context}\n\n[계획]\n${planData.synthesis}`,
  }))
  const resolved = []
  let round = 0
  while (unresolved.length > 0 && round < MAX_RESULT_ROUNDS) {
    round++
    const roundResults = await runResultRound(unresolved, parsedArgs.context, round)
    const stillUnresolved = []
    roundResults.forEach((r, idx) => {
      const isResolved = /resolved\s*[:：]\s*true/i.test(r)
      if (isResolved) {
        resolved.push({ issue: unresolved[idx].issue, result: r })
      } else {
        stillUnresolved.push({ issue: unresolved[idx].issue, history: r })
      }
    })
    unresolved = stillUnresolved
    log(`${prefix}Result ${round}라운드 종료 — 해결 ${resolved.length}개, 미해결 ${unresolved.length}개`)
  }

  return {
    stage: 'pipeline',
    status: 'complete',
    plan: planData,
    review: reviewData,
    reviewAttempts: reviewAttempt,
    resolved,
    unresolved: unresolved.map(u => u.issue),
    resultRounds: round,
  }
}

throw new Error(`알 수 없는 args.stage: ${parsedArgs.stage} (pipeline | plan | review | result)`)
