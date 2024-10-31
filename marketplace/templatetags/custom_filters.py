from django import template

register = template.Library()


def number_to_words(n):
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    teens = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm", "mười sáu", "mười bảy", "mười tám",
             "mười chín"]
    tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    thousands = ["", "nghìn", "triệu", "tỷ"]

    def words(n):
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + ('' if n % 10 == 0 else ' ' + units[n % 10])
        elif n < 1000:
            return units[n // 100] + " trăm" + ('' if n % 100 == 0 else ' ' + words(n % 100))
        else:
            for i in range(len(thousands)):
                if n < 1000 ** (i + 1):
                    return words(n // 1000 ** i) + " " + thousands[i] + (
                        '' if n % 1000 ** i == 0 else ' ' + words(n % 1000 ** i))

    return words(n)


@register.filter(name='to_vnd_words')
def to_vnd_words(value):
    try:
        value = int(value)
        result = number_to_words(value) + " đồng"
        result = result[0].upper() + result[1:]
        print('Kết quả:', result)
        return result
    except (ValueError, TypeError):
        return value
