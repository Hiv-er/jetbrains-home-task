import allure


class Helper:

    @staticmethod
    def attach_response(name, obj):
        try:
            content = str(obj)
            allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)
        except Exception:
            try:
                allure.attach(f"<failed to attach {name}>", name=f"{name} (attachment failed)",
                              attachment_type=allure.attachment_type.TEXT)
            except Exception:
                pass
