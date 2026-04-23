"use server";

import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";
import path from "path";
import * as cheerio from "cheerio";

// Initialize Gemini (Ensure API key is set in .env.local)
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "dummy_key_for_now");

async function extractTextFromUrl(url: string) {
  try {
    const response = await fetch(url);
    const html = await response.text();
    const $ = cheerio.load(html);
    // Remove scripts and styles
    $('script, style, nav, footer, header, aside').remove();
    const text = $('body').text().replace(/\s+/g, ' ').trim();
    return text.substring(0, 15000); // Send only up to ~15k chars to limit token usage
  } catch (error) {
    console.error("Failed to extract URL:", error);
    return null;
  }
}

export async function askCopilot(topic: string, category: string, userMessage: string, history: {role: string, parts: {text: string}[]}[] = []) {
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
    
    // Check if topic contains a URL
    let enrichedTopic = topic;
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = topic.match(urlRegex) || userMessage.match(urlRegex);

    if (urls && urls.length > 0) {
      const extractedText = await extractTextFromUrl(urls[0]);
      if (extractedText) {
        enrichedTopic += `\n\n[웹문서 추출 내용 요약 기반]:\n${extractedText.substring(0, 5000)}...`;
      }
    }
    
    let basePrompt = `너는 "Wook's AI and Marketing" 블로그의 수석 편집장 AI야. 현재 다루고 있는 카테고리는 "${category}"이고 주제는 "${enrichedTopic}"이야.`;
    
    if (category.includes("News") || category.includes("Yoon")) {
      basePrompt += `
[작업 방식: Yoon's AI 메일 연동 모드]
사용자가 던져준 오늘자 뉴스(Topic이나 내용)를 바탕으로, 즉시 블로그에 올릴 수 있는 '초안(Draft)'을 먼저 작성해서 보여줘. 사용자가 초안을 보고 코멘트를 남기며 수정 과정을 거치게 유도해.`;
    } else if (category.includes("논문")) {
      basePrompt += `
[작업 방식: 하루 마케팅 논문 추천 모드]
사용자가 '논문을 추천해달라'고 요청하면 제공된 논문의 내용과 시사점을 브리핑하고, 실무 관점의 질문을 던져서 대화를 리드해.`;

      if (userMessage.includes("오늘의 논문을 추천해주고 제안해줘")) {
        const dbPath = path.join(process.cwd(), "papers_db.json");
        if (fs.existsSync(dbPath)) {
          const papers = JSON.parse(fs.readFileSync(dbPath, "utf8"));
          const randomPaper = papers[Math.floor(Math.random() * papers.length)];
          userMessage = `오늘의 논문을 추천해줘. 추천 논문 데이터: 
제목: ${randomPaper.title}
저자: ${randomPaper.authors} (${randomPaper.year}, ${randomPaper.journal})
요약: ${randomPaper.abstract}`;
        }
      }
    } else {
      basePrompt += `
[작업 방식: 커리어 & 일반 모드]
마케터가 생각과 인사이트를 이끌어낼 수 있도록 날카로운 질문을 던지거나, 초안을 먼저 잡아줘. 충분히 대화가 무르익으면 한 편의 마크다운 글을 완성해서 보여줘.`;
    }

    const chatSession = model.startChat({
      history: history.length > 0 ? history : [
        {
          role: "user",
          parts: [{ text: basePrompt }],
        },
        {
          role: "model",
          parts: [{ text: "네! 원하시는 카테고리 로직에 맞게 초안을 먼저 작성하거나, 질문을 던져 인사이트를 끌어내겠습니다. 시작해 주세요!" }]
        }
      ],
      generationConfig: {
        temperature: 0.7,
      }
    });

    const result = await chatSession.sendMessage(userMessage);
    const response = await result.response;
    return { success: true, text: response.text() };
  } catch (error: any) {
    console.error("Gemini Error:", error);
    return { success: false, error: error.message };
  }
}

export async function publishPost(title: string, category: string, markdownContent: string) {
  try {
    const date = new Date().toISOString().split("T")[0];
    const safeTitle = title.toLowerCase().replace(/[^a-z0-9가-힣]/g, "-").replace(/-+/g, "-").substring(0, 30);
    const filename = `${date}-${safeTitle || "post"}.md`;
    
    let finalContent = markdownContent;
    if (!markdownContent.startsWith("---")) {
      const frontmatter = `---
title: "${title.replace(/"/g, '')}"
date: "${date}"
excerpt: "${markdownContent.substring(0, 100).replace(/\n/g, " ").replace(/"/g, "'")}..."
category: "${category}"
---

`;
      finalContent = frontmatter + markdownContent;
    }

    const filepath = path.join(process.cwd(), "content/posts", filename);
    fs.writeFileSync(filepath, finalContent, "utf8");
    
    return { success: true, filename };
  } catch (error: any) {
    console.error("Publish Error:", error);
    return { success: false, error: error.message };
  }
}

export async function loadYoonsAiData() {
  try {
    const yoonsAiPath = path.join(process.cwd(), "../yoons-ai-daily/daily_newsletter_summary.md");
    if (!fs.existsSync(yoonsAiPath)) {
      return { success: false, error: "Yoon's AI 뉴스레터 파일을 찾을 수 없습니다." };
    }
    const content = fs.readFileSync(yoonsAiPath, "utf8");
    return { success: true, data: content };
  } catch (error: any) {
    console.error("Load Error:", error);
    return { success: false, error: error.message };
  }
}
