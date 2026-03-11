<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-blue-100">
            作业详情
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">{{ assignment?.title || '作业加载中' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">查看题目、提交答案与评分反馈，并保持班级内作业流程统一。</p>
        </div>

        <div class="grid w-full max-w-md grid-cols-2 gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">题目数量</p>
            <p class="mt-2 text-3xl font-semibold">{{ problems.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前模式</p>
            <p class="mt-2 text-xl font-semibold">{{ canManageAssignments ? '教师视图' : '学生视图' }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="assignment" class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="space-y-4">
        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">作业说明</h3>
              <p class="mt-2 text-sm leading-6 text-slate-500">{{ assignment.description || '当前作业还没有补充说明。' }}</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
              @click="goBack"
            >
              返回班级作业
            </button>
            <button
              v-if="assignment && !canManageAssignments"
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-cyan-50 px-4 py-2 text-sm font-medium text-cyan-700 transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-100"
              @click="openAiTutor()"
            >
              打开 AI 助学
            </button>
          </div>

          <div class="mt-6 grid gap-4 md:grid-cols-3">
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">截止时间</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatDateTime(assignment.due_date) }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">创建时间</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatDateTime(assignment.created_at) }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">我的状态</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ canManageAssignments ? '教师管理中' : studentStatus }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">题目列表</h3>
              <p class="mt-1 text-sm text-slate-500">{{ canManageAssignments ? '教师可以在这里维护题目内容、顺序和分值。' : '根据题目类型展示对应的作答区域。' }}</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">共 {{ problems.length }} 题</span>
              <button
                v-if="canManageAssignments"
                type="button"
                class="rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100"
                @click="resetProblemForm"
              >
                {{ editingProblemId ? '新建题目' : '添加题目' }}
              </button>
            </div>
          </div>

          <div v-if="canManageAssignments" class="mt-6 rounded-[24px] border border-slate-200 bg-slate-50 p-5">
            <div>
              <h4 class="text-base font-semibold text-slate-900">{{ editingProblemId ? '编辑题目' : '新增题目' }}</h4>
              <p class="mt-1 text-sm text-slate-500">支持选择题、简答题和编程题三种类型。</p>
            </div>

            <div class="mt-5 grid gap-4 md:grid-cols-2">
              <label class="block space-y-2">
                <span class="text-sm font-medium text-slate-700">题型</span>
                <select v-model="problemForm.type" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500">
                  <option value="choice">选择题</option>
                  <option value="short_answer">简答题</option>
                  <option value="coding">编程题</option>
                </select>
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-slate-700">显示顺序</span>
                <input v-model.number="problemForm.display_order" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500" />
              </label>

              <label class="block space-y-2 md:col-span-2">
                <span class="text-sm font-medium text-slate-700">题目内容</span>
                <textarea v-model.trim="problemForm.content" rows="4" class="w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-blue-500"></textarea>
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-slate-700">分值</span>
                <input v-model.number="problemForm.score" type="number" min="1" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500" />
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-slate-700">参考答案</span>
                <input v-model.trim="problemForm.correct_answer" type="text" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500" placeholder="可选" />
              </label>

              <div v-if="problemForm.type === 'choice'" class="space-y-3 md:col-span-2">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-sm font-medium text-slate-700">选项列表</span>
                  <button type="button" class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100" @click="addChoiceOption">添加选项</button>
                </div>
                <div class="space-y-3">
                  <div v-for="(option, optionIndex) in problemForm.options" :key="`option-${optionIndex}`" class="flex items-center gap-3 rounded-2xl bg-white px-4 py-3" :class="option.trim() ? 'border border-slate-200' : 'border border-amber-200'">
                    <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ String.fromCharCode(65 + optionIndex) }}</span>
                    <input v-model.trim="problemForm.options[optionIndex]" type="text" class="flex-1 border-none bg-transparent text-sm text-slate-900 outline-none" placeholder="输入选项内容" />
                    <button type="button" class="rounded-2xl px-3 py-2 text-xs font-medium text-rose-600 transition hover:bg-rose-50 disabled:cursor-not-allowed disabled:text-rose-300" :disabled="problemForm.options.length <= 2" @click="removeChoiceOption(optionIndex)">删除</button>
                  </div>
                </div>
                <p class="text-xs text-slate-400">至少保留两个有效选项，参考答案需与某个选项完全一致。</p>
              </div>

              <label v-if="problemForm.type === 'coding'" class="block space-y-2 md:col-span-2">
                <span class="text-sm font-medium text-slate-700">代码模板</span>
                <textarea v-model.trim="problemForm.code_template" rows="6" class="w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 font-mono text-sm leading-6 text-slate-900 outline-none transition focus:border-blue-500"></textarea>
              </label>

              <div v-if="problemForm.type === 'coding'" class="space-y-3 md:col-span-2">
                <div class="flex items-center justify-between gap-3">
                  <span class="text-sm font-medium text-slate-700">测试用例</span>
                  <button type="button" class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100" @click="addTestCase">添加用例</button>
                </div>
                <div class="space-y-3">
                  <div v-for="(testCase, caseIndex) in problemForm.test_cases" :key="`test-case-${caseIndex}`" class="rounded-3xl border p-4" :class="testCase.input.trim() || testCase.output.trim() ? 'border-slate-200 bg-white' : 'border-amber-200 bg-amber-50/40'">
                    <div class="flex items-center justify-between gap-3">
                      <span class="text-xs font-medium text-slate-500">用例 {{ caseIndex + 1 }}</span>
                      <button type="button" class="rounded-2xl px-3 py-2 text-xs font-medium text-rose-600 transition hover:bg-rose-50 disabled:cursor-not-allowed disabled:text-rose-300" :disabled="problemForm.test_cases.length <= 1" @click="removeTestCase(caseIndex)">删除</button>
                    </div>
                    <div class="mt-3 grid gap-3 md:grid-cols-2">
                      <label class="block space-y-2">
                        <span class="text-xs font-medium text-slate-500">输入</span>
                        <textarea v-model.trim="testCase.input" rows="4" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 font-mono text-sm leading-6 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white" placeholder="标准输入"></textarea>
                      </label>
                      <label class="block space-y-2">
                        <span class="text-xs font-medium text-slate-500">输出</span>
                        <textarea v-model.trim="testCase.output" rows="4" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 font-mono text-sm leading-6 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white" placeholder="期望输出"></textarea>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-5 rounded-[24px] border border-dashed border-slate-300 bg-white/80 p-5">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-semibold text-slate-900">题目预览</p>
                  <p class="mt-1 text-xs text-slate-500">保存前快速检查题干、选项和测试用例展示效果。</p>
                </div>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ problemTypeLabel(problemForm.type) }}</span>
              </div>
              <div class="mt-4 space-y-4">
                <div>
                  <p class="text-base font-semibold text-slate-900">{{ problemPreviewTitle }}</p>
                  <p class="mt-2 text-sm text-slate-500">分值 {{ problemForm.score }} 分 · 顺序 {{ problemForm.display_order }}</p>
                </div>
                <div v-if="problemForm.type === 'choice'" class="space-y-2">
                  <div v-for="(option, optionIndex) in normalizedChoiceOptions" :key="`preview-option-${optionIndex}`" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    {{ String.fromCharCode(65 + optionIndex) }}. {{ option }}
                  </div>
                  <p v-if="problemForm.correct_answer.trim()" class="text-xs text-emerald-600">参考答案：{{ problemForm.correct_answer.trim() }}</p>
                </div>
                <div v-else-if="problemForm.type === 'coding'" class="space-y-3">
                  <pre v-if="problemForm.code_template.trim()" class="overflow-x-auto rounded-2xl border border-slate-200 bg-slate-900 p-4 font-mono text-xs leading-6 text-slate-100">{{ problemForm.code_template.trim() }}</pre>
                  <div v-if="normalizedTestCases.length" class="grid gap-3 md:grid-cols-2">
                    <div v-for="(testCase, caseIndex) in normalizedTestCases" :key="`preview-test-case-${caseIndex}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">用例 {{ caseIndex + 1 }}</p>
                      <p class="mt-3 text-xs font-medium text-slate-500">输入</p>
                      <pre class="mt-1 whitespace-pre-wrap rounded-2xl bg-white p-3 font-mono text-xs text-slate-700">{{ testCase.input || '空' }}</pre>
                      <p class="mt-3 text-xs font-medium text-slate-500">输出</p>
                      <pre class="mt-1 whitespace-pre-wrap rounded-2xl bg-white p-3 font-mono text-xs text-slate-700">{{ testCase.output || '空' }}</pre>
                    </div>
                  </div>
                </div>
                <p v-else class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-700">{{ problemForm.correct_answer.trim() || '简答题暂无参考答案，学生将看到题目内容并直接作答。' }}</p>
              </div>
            </div>

            <div class="mt-5 flex gap-3">
              <button v-if="editingProblemId" type="button" class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100" @click="resetProblemForm">取消编辑</button>
              <button type="button" class="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400" :disabled="problemSaving" @click="handleSaveProblem">
                {{ problemSaving ? '保存中...' : editingProblemId ? '保存题目' : '添加题目' }}
              </button>
            </div>
          </div>

          <div v-if="loading" class="mt-6 space-y-4">
            <div v-for="index in 3" :key="index" class="animate-pulse rounded-2xl bg-slate-50 p-5">
              <div class="h-5 w-40 rounded bg-slate-200"></div>
              <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
              <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
            </div>
          </div>

          <div v-else-if="problems.length" class="mt-6 space-y-4">
            <article
              v-for="(problem, index) in orderedProblems"
              :key="problem.id"
              class="rounded-2xl border border-slate-200 bg-slate-50 p-5"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <div class="flex items-center gap-3">
                    <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">第 {{ index + 1 }} 题</span>
                    <span class="rounded-full bg-slate-200 px-3 py-1 text-xs font-medium text-slate-700">{{ problemTypeLabel(problem.type) }}</span>
                  </div>
                  <h4 class="mt-4 text-base font-semibold text-slate-900">{{ problem.content }}</h4>
                </div>
                <div class="flex items-center gap-3">
                  <span class="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600 shadow-sm">{{ problem.score }} 分</span>
                  <template v-if="canManageAssignments">
                    <button type="button" class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-300" :disabled="index === 0 || reorderingProblemId === problem.id" @click="handleMoveProblem(problem.id, 'up')">{{ reorderingProblemId === problem.id ? '调整中...' : '上移' }}</button>
                    <button type="button" class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-300" :disabled="index === orderedProblems.length - 1 || reorderingProblemId === problem.id" @click="handleMoveProblem(problem.id, 'down')">{{ reorderingProblemId === problem.id ? '调整中...' : '下移' }}</button>
                    <button type="button" class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100" @click="startEditProblem(problem)">编辑</button>
                    <button type="button" class="rounded-2xl bg-rose-600 px-3 py-2 text-xs font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-400" :disabled="deletingProblemId === problem.id" @click="handleDeleteProblem(problem.id)">{{ deletingProblemId === problem.id ? '删除中...' : '删除' }}</button>
                  </template>
                </div>
              </div>

              <div class="mt-5">
                <div v-if="problem.type === 'choice'" class="space-y-3">
                  <label
                    v-for="(option, optionIndex) in problem.options"
                    :key="`${problem.id}-${optionIndex}`"
                    class="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 transition-all duration-300 hover:border-blue-200 hover:bg-blue-50"
                  >
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-500">{{ String.fromCharCode(65 + optionIndex) }}</span>
                    <input
                      :checked="String(answers[problem.id] || '') === option"
                      type="radio"
                      :name="`problem-${problem.id}`"
                      class="h-4 w-4 border-slate-300 text-blue-600"
                      :disabled="canManageAssignments"
                      @change="updateAnswer(problem.id, option)"
                    />
                    {{ option }}
                  </label>
                  <p v-if="canManageAssignments && problem.correct_answer" class="text-xs text-emerald-600">参考答案：{{ problem.correct_answer }}</p>
                </div>

                <div v-else-if="problem.type === 'coding'" class="space-y-4">
                  <pre v-if="problem.code_template" class="overflow-x-auto rounded-2xl border border-slate-200 bg-slate-900 p-4 font-mono text-xs leading-6 text-slate-100">{{ problem.code_template }}</pre>
                  <div v-if="problem.test_cases.length && canManageAssignments" class="grid gap-3 md:grid-cols-2">
                    <div v-for="(testCase, caseIndex) in problem.test_cases" :key="`${problem.id}-test-${caseIndex}`" class="rounded-2xl border border-slate-200 bg-white p-4">
                      <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">用例 {{ caseIndex + 1 }}</p>
                      <p class="mt-3 text-xs font-medium text-slate-500">输入</p>
                      <pre class="mt-1 whitespace-pre-wrap rounded-2xl bg-slate-50 p-3 font-mono text-xs text-slate-700">{{ testCase.input || '空' }}</pre>
                      <p class="mt-3 text-xs font-medium text-slate-500">输出</p>
                      <pre class="mt-1 whitespace-pre-wrap rounded-2xl bg-slate-50 p-3 font-mono text-xs text-slate-700">{{ testCase.output || '空' }}</pre>
                    </div>
                  </div>
                  <textarea
                    :value="String(answers[problem.id] || problem.code_template || '')"
                    rows="10"
                    class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 font-mono text-sm leading-6 text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                    placeholder="请输入代码答案"
                    :disabled="canManageAssignments"
                    @input="updateAnswer(problem.id, ($event.target as HTMLTextAreaElement).value)"
                  ></textarea>
                </div>

                <textarea
                  v-else
                  :value="String(answers[problem.id] || problem.code_template || '')"
                  rows="5"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                  placeholder="请输入文字答案"
                  :disabled="canManageAssignments"
                  @input="updateAnswer(problem.id, ($event.target as HTMLTextAreaElement).value)"
                ></textarea>

                <div v-if="!canManageAssignments" class="mt-4 flex flex-wrap gap-3">
                  <button
                    type="button"
                    class="rounded-2xl border border-cyan-200 bg-cyan-50 px-4 py-2 text-sm font-medium text-cyan-700 transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-100"
                    @click="openAiTutor(problem.id, problem.type === 'coding' ? 'code_review' : 'hint')"
                  >
                    {{ problem.type === 'coding' ? 'AI 解释代码问题' : 'AI 提示这道题' }}
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
            <p class="text-sm font-medium text-slate-700">当前作业还没有题目</p>
            <p class="mt-2 text-sm text-slate-400">{{ canManageAssignments ? '先创建第一道题，学生才能进入作答。' : '教师添加题目后，这里会自动展示。' }}</p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div v-if="canManageAssignments && assignment" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">作业设置</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">修改作业标题、说明和截止时间，或直接删除该作业。</p>
          </div>

          <div class="mt-5 space-y-4">
            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">作业标题</span>
              <input v-model.trim="assignmentForm.title" type="text" class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100" />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">作业说明</span>
              <textarea v-model.trim="assignmentForm.description" rows="4" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"></textarea>
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">截止时间</span>
              <input v-model="assignmentForm.due_date" type="datetime-local" class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100" />
            </label>

            <div class="flex gap-3">
              <button type="button" class="flex h-[52px] flex-1 items-center justify-center rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400" :disabled="assignmentSaving" @click="handleSaveAssignmentMeta">{{ assignmentSaving ? '保存中...' : '保存作业设置' }}</button>
              <button type="button" class="flex h-[52px] items-center justify-center rounded-2xl bg-rose-600 px-4 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-400" :disabled="assignmentDeleting" @click="handleDeleteAssignment">{{ assignmentDeleting ? '删除中...' : '删除作业' }}</button>
            </div>
          </div>
        </div>

        <div v-if="!canManageAssignments" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">提交作业</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">提交后可以再次覆盖更新答案，系统会保留最近一次提交。</p>
          </div>

          <div class="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">
            <p>当前状态：{{ studentStatus }}</p>
            <p class="mt-2">最近提交：{{ mySubmission ? formatDateTime(mySubmission.submitted_at) : '尚未提交' }}</p>
            <p class="mt-2">教师评分：{{ mySubmission?.score ?? '待评分' }}</p>
            <p v-if="mySubmission?.feedback" class="mt-2">教师评语：{{ mySubmission.feedback }}</p>
          </div>

          <button
            type="button"
            class="mt-5 flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-blue-400"
            :disabled="submitting || !problems.length"
            @click="handleSubmit"
          >
            <span v-if="submitting" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
            {{ submitting ? '提交中...' : mySubmission ? '更新提交' : '提交作业' }}
          </button>
        </div>

        <div v-else class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">提交记录</h3>
              <p class="mt-1 text-sm text-slate-500">教师端查看学生提交并完成评分。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100"
              @click="loadSubmissions"
            >
              刷新提交
            </button>
          </div>

          <div v-if="submissionsLoading" class="mt-6 space-y-3">
            <div v-for="index in 3" :key="index" class="animate-pulse rounded-2xl bg-slate-50 p-4">
              <div class="h-4 w-24 rounded bg-slate-200"></div>
              <div class="mt-2 h-4 w-40 rounded bg-slate-200"></div>
            </div>
          </div>

          <div v-else-if="submissions.length" class="mt-6 space-y-3">
            <button
              v-for="submission in submissions"
              :key="submission.id"
              type="button"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-left transition-all duration-300 hover:-translate-y-1 hover:border-blue-200 hover:bg-white"
              @click="selectSubmission(submission)"
            >
              <div class="flex items-center justify-between gap-4">
                <div>
                  <p class="text-sm font-semibold text-slate-900">{{ submission.student_name || `学生 #${submission.student_id}` }}</p>
                  <p class="mt-1 text-sm text-slate-500">提交时间：{{ formatDateTime(submission.submitted_at) }}</p>
                </div>
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="submission.score !== null && submission.score !== undefined ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
                  {{ submission.score !== null && submission.score !== undefined ? `${submission.score} 分` : '待评分' }}
                </span>
              </div>
            </button>
          </div>

          <div v-else class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
            <p class="text-sm font-medium text-slate-700">暂时还没有学生提交</p>
            <p class="mt-2 text-sm text-slate-400">学生提交作业后，这里会自动展示最新记录。</p>
          </div>
        </div>

        <div v-if="selectedSubmission && canManageAssignments" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">批改作业</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">当前学生：{{ selectedSubmission.student_name || `学生 #${selectedSubmission.student_id}` }}</p>
          </div>

          <div class="mt-5 space-y-4">
            <div v-for="problem in orderedProblems" :key="problem.id" class="rounded-2xl bg-slate-50 p-4">
              <p class="text-sm font-semibold text-slate-900">{{ problem.content }}</p>
              <pre class="mt-3 whitespace-pre-wrap rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-700">{{ renderSubmissionAnswer(selectedSubmission.answers[problem.id]) }}</pre>
            </div>
          </div>

          <div class="mt-5 space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">评分</label>
              <input
                v-model.number="gradeForm.score"
                type="number"
                min="0"
                class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              />
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">评语</label>
              <textarea
                v-model="gradeForm.feedback"
                rows="4"
                placeholder="输入批改意见"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              ></textarea>
            </div>

            <button
              type="button"
              class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="grading"
              @click="handleGrade"
            >
              <span v-if="grading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ grading ? '保存中...' : '提交评分' }}
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  createProblem,
  deleteAssignment,
  deleteProblem,
  getAssignment,
  getMySubmission,
  getSubmissions,
  gradeSubmission,
  listProblems,
  submitAssignment,
  updateAssignment,
  updateProblem,
  type Assignment,
  type Problem,
  type ProblemPayload,
  type Submission,
} from '@/services/assignments';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const assignmentId = Number(route.params.id);
const loading = ref(false);
const submissionsLoading = ref(false);
const submitting = ref(false);
const grading = ref(false);
const assignmentSaving = ref(false);
const assignmentDeleting = ref(false);
const problemSaving = ref(false);
const deletingProblemId = ref<number | null>(null);
const reorderingProblemId = ref<number | null>(null);
const editingProblemId = ref<number | null>(null);
const assignment = ref<Assignment | null>(null);
const problems = ref<Problem[]>([]);
const mySubmission = ref<Submission | null>(null);
const submissions = ref<Submission[]>([]);
const selectedSubmission = ref<Submission | null>(null);
const answers = ref<Record<number, unknown>>({});
const gradeForm = ref({
  score: 0,
  feedback: '',
});
const assignmentForm = ref({
  title: '',
  description: '',
  due_date: '',
});
const problemForm = ref({
  type: 'choice' as Problem['type'],
  content: '',
  score: 10,
  display_order: 0,
  options: ['', ''],
  correct_answer: '',
  code_template: '',
  test_cases: [{ input: '', output: '' }],
});

const canManageAssignments = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');
const orderedProblems = computed(() => [...problems.value].sort((left, right) => left.display_order - right.display_order));
const normalizedChoiceOptions = computed(() => problemForm.value.options.map((item) => item.trim()).filter(Boolean));
const normalizedTestCases = computed(() => problemForm.value.test_cases.map((item) => ({ input: item.input.trim(), output: item.output.trim() })).filter((item) => item.input || item.output));
const problemPreviewTitle = computed(() => problemForm.value.content.trim() || '题目预览会显示在这里');
const studentStatus = computed(() => {
  if (!mySubmission.value) {
    return '待提交';
  }

  if (mySubmission.value.score !== null && mySubmission.value.score !== undefined) {
    return `已评分 ${mySubmission.value.score} 分`;
  }

  return '已提交待评分';
});

const problemTypeLabel = (type: Problem['type']) => {
  if (type === 'choice') return '选择题';
  if (type === 'coding') return '编程题';
  return '简答题';
};

const formatDateTime = (value?: string | null) => {
  if (!value) {
    return '未设置';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

const updateAnswer = (problemId: number, value: unknown) => {
  answers.value = {
    ...answers.value,
    [problemId]: value,
  };
};

const renderSubmissionAnswer = (value: unknown) => {
  if (value === null || value === undefined || value === '') {
    return '无作答';
  }

  if (typeof value === 'string') {
    return value;
  }

  return JSON.stringify(value, null, 2);
};

const syncAssignmentForm = () => {
  if (!assignment.value) {
    return;
  }

  assignmentForm.value = {
    title: assignment.value.title,
    description: assignment.value.description || '',
    due_date: assignment.value.due_date ? new Date(assignment.value.due_date).toISOString().slice(0, 16) : '',
  };
};

const buildProblemPayload = (): ProblemPayload => {
  return {
    type: problemForm.value.type,
    content: problemForm.value.content.trim(),
    score: Number(problemForm.value.score),
    display_order: Number(problemForm.value.display_order),
    options: problemForm.value.type === 'choice' ? normalizedChoiceOptions.value : [],
    correct_answer: problemForm.value.correct_answer.trim() || null,
    code_template: problemForm.value.type === 'coding' ? (problemForm.value.code_template.trim() || null) : null,
    test_cases: problemForm.value.type === 'coding' ? normalizedTestCases.value : [],
  };
};

const resetProblemForm = () => {
  editingProblemId.value = null;
  problemForm.value = {
    type: 'choice',
    content: '',
    score: 10,
    display_order: problems.value.length,
    options: ['', ''],
    correct_answer: '',
    code_template: '',
    test_cases: [{ input: '', output: '' }],
  };
};

const startEditProblem = (problem: Problem) => {
  editingProblemId.value = problem.id;
  problemForm.value = {
    type: problem.type,
    content: problem.content,
    score: problem.score,
    display_order: problem.display_order,
    options: problem.options.length ? [...problem.options] : ['', ''],
    correct_answer: problem.correct_answer || '',
    code_template: problem.code_template || '',
    test_cases: problem.test_cases.length
      ? problem.test_cases.map((item) => ({ input: item.input || '', output: item.output || '' }))
      : [{ input: '', output: '' }],
  };
};

const ensureMinimumChoiceOptions = () => {
  if (problemForm.value.options.length >= 2) {
    return;
  }

  while (problemForm.value.options.length < 2) {
    problemForm.value.options.push('');
  }
};

const ensureMinimumTestCases = () => {
  if (problemForm.value.test_cases.length > 0) {
    return;
  }

  problemForm.value.test_cases.push({ input: '', output: '' });
};

const addChoiceOption = () => {
  problemForm.value.options.push('');
};

const removeChoiceOption = (index: number) => {
  problemForm.value.options.splice(index, 1);
  ensureMinimumChoiceOptions();
};

const addTestCase = () => {
  problemForm.value.test_cases.push({ input: '', output: '' });
};

const removeTestCase = (index: number) => {
  problemForm.value.test_cases.splice(index, 1);
  ensureMinimumTestCases();
};

const syncEditingProblemOrder = () => {
  if (!editingProblemId.value) {
    return;
  }

  const currentProblem = problems.value.find((item) => item.id === editingProblemId.value);
  if (currentProblem) {
    problemForm.value.display_order = currentProblem.display_order;
  }
};

const handleMoveProblem = async (problemId: number, direction: 'up' | 'down') => {
  const problemIndex = orderedProblems.value.findIndex((item) => item.id === problemId);
  if (problemIndex < 0) {
    return;
  }

  const targetIndex = direction === 'up' ? problemIndex - 1 : problemIndex + 1;
  if (targetIndex < 0 || targetIndex >= orderedProblems.value.length) {
    return;
  }

  const currentProblem = orderedProblems.value[problemIndex];
  const targetProblem = orderedProblems.value[targetIndex];
  if (!currentProblem || !targetProblem) {
    return;
  }

  reorderingProblemId.value = problemId;
  try {
    await Promise.all([
      updateProblem(assignmentId, currentProblem.id, { display_order: targetProblem.display_order }),
      updateProblem(assignmentId, targetProblem.id, { display_order: currentProblem.display_order }),
    ]);
    problems.value = await listProblems(assignmentId);
    syncEditingProblemOrder();
    ElMessage.success(direction === 'up' ? '题目已上移' : '题目已下移');
  } finally {
    reorderingProblemId.value = null;
  }
};

const loadSubmissions = async () => {
  if (!canManageAssignments.value) {
    return;
  }

  submissionsLoading.value = true;
  try {
    submissions.value = await getSubmissions(assignmentId, 1, 50);
  } finally {
    submissionsLoading.value = false;
  }
};

const loadData = async () => {
  loading.value = true;
  try {
    const [assignmentDetail, problemList] = await Promise.all([
      getAssignment(assignmentId),
      listProblems(assignmentId),
    ]);
    assignment.value = assignmentDetail;
    problems.value = problemList;
    syncAssignmentForm();
    resetProblemForm();

    if (canManageAssignments.value) {
      await loadSubmissions();
    } else {
      mySubmission.value = await getMySubmission(assignmentId);
      if (mySubmission.value?.answers) {
        const normalizedAnswers: Record<number, unknown> = {};
        for (const [key, value] of Object.entries(mySubmission.value.answers)) {
          normalizedAnswers[Number(key)] = value;
        }
        answers.value = normalizedAnswers;
      }
    }
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  submitting.value = true;
  try {
    const payload: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(answers.value)) {
      payload[String(key)] = value;
    }
    mySubmission.value = await submitAssignment(assignmentId, payload);
    ElMessage.success('作业提交成功');
  } finally {
    submitting.value = false;
  }
};

const handleSaveAssignmentMeta = async () => {
  if (!assignment.value) {
    return;
  }

  if (!assignmentForm.value.title.trim()) {
    ElMessage.warning('作业标题不能为空');
    return;
  }

  assignmentSaving.value = true;
  try {
    assignment.value = await updateAssignment(assignmentId, {
      title: assignmentForm.value.title.trim(),
      description: assignmentForm.value.description.trim() || undefined,
      due_date: assignmentForm.value.due_date ? new Date(assignmentForm.value.due_date).toISOString() : null,
    });
    syncAssignmentForm();
    ElMessage.success('作业设置已更新');
  } finally {
    assignmentSaving.value = false;
  }
};

const handleDeleteAssignment = async () => {
  if (!assignment.value) {
    return;
  }

  await ElMessageBox.confirm('删除后该作业、题目和所有提交记录都会被移除，是否继续？', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  });

  assignmentDeleting.value = true;
  try {
    const classroomId = assignment.value.classroom_id;
    await deleteAssignment(assignmentId);
    ElMessage.success('作业已删除');
    router.push(`/classes/${classroomId}/assignments`);
  } finally {
    assignmentDeleting.value = false;
  }
};

const handleSaveProblem = async () => {
  if (!problemForm.value.content.trim()) {
    ElMessage.warning('题目内容不能为空');
    return;
  }

  if (problemForm.value.type === 'choice' && normalizedChoiceOptions.value.length < 2) {
    ElMessage.warning('选择题至少需要两个有效选项');
    return;
  }

  if (
    problemForm.value.type === 'choice' &&
    problemForm.value.correct_answer.trim() &&
    !normalizedChoiceOptions.value.includes(problemForm.value.correct_answer.trim())
  ) {
    ElMessage.warning('选择题参考答案需要与选项内容完全一致');
    return;
  }

  problemSaving.value = true;
  try {
    const payload = buildProblemPayload();
    if (editingProblemId.value) {
      await updateProblem(assignmentId, editingProblemId.value, payload);
      ElMessage.success('题目已更新');
    } else {
      await createProblem(assignmentId, payload);
      ElMessage.success('题目已创建');
    }
    resetProblemForm();
    problems.value = await listProblems(assignmentId);
  } finally {
    problemSaving.value = false;
  }
};

const handleDeleteProblem = async (problemId: number) => {
  await ElMessageBox.confirm('删除后该题将不再出现在作业中，是否继续？', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  });

  deletingProblemId.value = problemId;
  try {
    await deleteProblem(assignmentId, problemId);
    problems.value = problems.value.filter((item) => item.id !== problemId);
    if (editingProblemId.value === problemId) {
      resetProblemForm();
    }
    ElMessage.success('题目已删除');
  } finally {
    deletingProblemId.value = null;
  }
};

const selectSubmission = (submission: Submission) => {
  selectedSubmission.value = submission;
  gradeForm.value.score = submission.score ?? 0;
  gradeForm.value.feedback = submission.feedback ?? '';
};

const handleGrade = async () => {
  if (!selectedSubmission.value) {
    return;
  }

  grading.value = true;
  try {
    const updated = await gradeSubmission(
      assignmentId,
      selectedSubmission.value.id,
      gradeForm.value.score,
      gradeForm.value.feedback,
    );
    ElMessage.success('评分已保存');
    selectedSubmission.value = updated;
    await loadSubmissions();
  } finally {
    grading.value = false;
  }
};

const goBack = () => {
  if (assignment.value) {
    router.push(`/classes/${assignment.value.classroom_id}/assignments`);
    return;
  }

  router.push('/classes');
};

const openAiTutor = (problemId?: number, mode: 'hint' | 'code_review' = 'hint') => {
  if (!assignment.value) {
    return;
  }

  router.push({
    path: `/classes/${assignment.value.classroom_id}/ai-tutor`,
    query: {
      assignmentId: String(assignment.value.id),
      problemId: problemId ? String(problemId) : undefined,
      mode,
    },
  });
};

onMounted(() => {
  loadData();
});

watch(
  () => problemForm.value.type,
  (nextType) => {
    if (nextType === 'choice') {
      ensureMinimumChoiceOptions();
    }

    if (nextType === 'coding') {
      ensureMinimumTestCases();
    }
  },
);
</script>
