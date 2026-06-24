import http from './http'

/** 实训成果智能核查。返回结构化结果 { function_check, logic_check, step_check, standard_score, standard_suggestion, summary } */
export const aiReview = (data) => http.post('/ai/review', data)
