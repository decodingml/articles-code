from articles.generative_ai.data_extraction_from_social_media_posts_using_llms.src.report_generator import ReportGenerator


def main():
    report_generator = ReportGenerator()
    report_filename = report_generator.generate_report()
    print(f"Report generated: {report_filename}")


if __name__ == "__main__":
    main()
