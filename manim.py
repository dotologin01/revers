from manim import *
import numpy as np

class PEVirtualMemoryMapping(Scene):
    def construct(self):
        self.camera.background_color = "#0B0E14"

        # Цветовая палитра для чёткого разделения процессов
        NOTEPAD_COLOR = "#00E5FF"      # Яркий голубой (Cyan) для Notepad.exe
        NOTEPAD_FILL  = "#004D61"
        MYAPP_COLOR   = "#FFB300"      # Контрастный оранжево-золотой (Amber) для MyApp.exe
        MYAPP_FILL    = "#5C3D00"
        RAM_COLOR     = "#2E7D32"      # Спокойный зелёный для общей структуры RAM

        # -------------------------------------------------------------
        # Вспомогательная функция для построения ортогональной стрелки (90 градусов)
        # -------------------------------------------------------------
        def create_ortho_arrow(points, color, stroke_width=2.8, tip_length=0.18):
            group = VGroup()
            for i in range(len(points) - 2):
                seg = Line(
                    points[i], points[i + 1],
                    color=color, stroke_width=stroke_width
                )
                group.add(seg)
            last_arrow = Arrow(
                points[-2], points[-1],
                color=color,
                stroke_width=stroke_width,
                buff=0,
                max_tip_length_to_length_ratio=1.0,
                tip_length=tip_length
            )
            group.add(last_arrow)
            return group

        # -------------------------------------------------------------
        # Вспомогательная функция для создания таблиц памяти одинаковых пропорций
        # -------------------------------------------------------------
        def create_memory_column(
            title, addresses, highlight_idx=-1,
            col_color=BLUE, highlight_stroke=WHITE, highlight_fill=PURPLE,
            title_color=WHITE, width=3.0, total_height=2.0
        ):
            group = VGroup()
            title_lbl = Text(title, font_size=15, color=title_color)
            group.add(title_lbl)

            cell_height = total_height / len(addresses)
            cells = VGroup()
            for i, addr in enumerate(addresses):
                is_hl = (i == highlight_idx)
                f_col = highlight_fill if is_hl else "#141C2B"
                f_op = 0.75 if is_hl else 0.85
                s_col = highlight_stroke if is_hl else col_color

                rect = Rectangle(
                    width=width,
                    height=cell_height,
                    stroke_color=s_col,
                    stroke_width=1.5 if not is_hl else 2.8,
                    fill_color=f_col,
                    fill_opacity=f_op
                )
                if i > 0:
                    rect.next_to(cells[i - 1][0], DOWN, buff=0)

                txt = Text(addr, font_size=11, color=WHITE if is_hl else GRAY_A)
                txt.move_to(rect.get_center())
                cells.add(VGroup(rect, txt))

            title_lbl.next_to(cells, UP, buff=0.18)
            subtitle_lbl = Text(
                "Виртуальные адреса" if "exe" in title else "Физические адреса",
                font_size=11,
                color=title_color if "exe" in title else GREEN_C
            )
            subtitle_lbl.next_to(cells, DOWN, buff=0.14)
            group.add(cells, subtitle_lbl)
            return group, cells

        # -------------------------------------------------------------
        # 1. Виртуальная память Notepad.exe (Слева, Голубая тема)
        # -------------------------------------------------------------
        notepad_addrs = [
            "0x7F793950000",  # [0] целевая страница
            "0x7F793951000",
            "0x7F793952000",
            "0x7FF7FFFFFFF"
        ]
        notepad_col, np_cells = create_memory_column(
            "Notepad.exe", notepad_addrs, highlight_idx=0,
            col_color="#1A5263", highlight_stroke=NOTEPAD_COLOR, highlight_fill=NOTEPAD_FILL,
            title_color=NOTEPAD_COLOR, width=3.0, total_height=2.0
        )
        notepad_col.move_to([-4.6, 1.15, 0])

        # -------------------------------------------------------------
        # 2. Виртуальная память MyApp.exe (Справа, Оранжево-золотая тема)
        # -------------------------------------------------------------
        myapp_addrs = [
            "0x7F793950000",  # [0] целевая страница
            "0x7F793951000",
            "0x7F793952000",
            "0x7FF7FFFFFFF"
        ]
        myapp_col, my_cells = create_memory_column(
            "MyApp.exe", myapp_addrs, highlight_idx=0,
            col_color="#664614", highlight_stroke=MYAPP_COLOR, highlight_fill=MYAPP_FILL,
            title_color=MYAPP_COLOR, width=3.0, total_height=2.0
        )
        myapp_col.move_to([4.6, 1.15, 0])

        # -------------------------------------------------------------
        # 3. Физическая память (Сверху посередине, с нулевой страницей P0)
        # -------------------------------------------------------------
        ram_addrs = [
            "0x00000000 (P0)", # [0] Нулевая страница только в физ. памяти
            "0x33CE0000",      # [1] слот для MyApp (Оранжево-золотой)
            "0x63A20000",      # [2]
            "0xAFDA0000",      # [3]
            "0xBC650000"       # [4] слот для Notepad (Голубой)
        ]
        ram_col, ram_cells = create_memory_column(
            "Физическая память (RAM)", ram_addrs, highlight_idx=-1,
            col_color=RAM_COLOR, title_color=WHITE, width=3.0, total_height=2.0
        )
        # Окрашиваем физические слоты в цвета соответствующих программ:
        # Ячейка [1] (0x33CE0000) -> под цвет MyApp.exe
        ram_cells[1][0].set_fill(MYAPP_FILL, opacity=0.75).set_stroke(MYAPP_COLOR, 2.2)
        ram_cells[1][1].set_color(WHITE)
        # Ячейка [4] (0xBC650000) -> под цвет Notepad.exe
        ram_cells[4][0].set_fill(NOTEPAD_FILL, opacity=0.75).set_stroke(NOTEPAD_COLOR, 2.2)
        ram_cells[4][1].set_color(WHITE)

        ram_col.move_to([0, 1.15, 0])

        # -------------------------------------------------------------
        # 4. Иконка планки оперативной памяти (над блоком физической памяти)
        # -------------------------------------------------------------
        ram_stick = VGroup()
        pcb = Rectangle(width=3.0, height=0.38, color=GREEN_E, fill_color="#0F381E", fill_opacity=0.95)
        chips = VGroup(*[
            Rectangle(width=0.40, height=0.17, color=DARK_GRAY, fill_color="#1F1F1F", fill_opacity=0.9)
            .move_to([-0.93 + i * 0.62, 0.04, 0])
            for i in range(4)
        ])
        pins = VGroup(*[
            Rectangle(width=0.09, height=0.06, color=YELLOW_C, fill_color=YELLOW_C, fill_opacity=1.0)
            .move_to([-1.20 + i * 0.24, -0.14, 0])
            for i in range(11)
        ])
        ddr_label = Text("DDR RAM", font_size=9, color=YELLOW_C).move_to([0, 0.04, 0])
        ram_stick.add(pcb, chips, pins, ddr_label)
        ram_stick.next_to(ram_col[0], UP, buff=0.15)

        # -------------------------------------------------------------
        # 5. ЕДИНЫЙ блок ЦП (CPU) с интегрированным MMU внизу посередине
        # -------------------------------------------------------------
        cpu_box = RoundedRectangle(
            corner_radius=0.12, width=4.2, height=1.55,
            color=GRAY_C, fill_color="#161B22", fill_opacity=0.95
        )
        cpu_lbl = Text("Центральный процессор (CPU)", font_size=12, color=GRAY_A).next_to(cpu_box.get_top(), DOWN, buff=0.1)

        mmu_box = RoundedRectangle(
            corner_radius=0.08, width=3.7, height=0.95,
            color=TEAL_C, fill_color="#0E3338", fill_opacity=0.95
        ).next_to(cpu_lbl, DOWN, buff=0.08)

        mmu_title = Text("MMU (Блок управления памятью)", font_size=11, color=TEAL_A).next_to(mmu_box.get_top(), DOWN, buff=0.08)
        lookup_status = Text(
            "Lookup Table (Таблица страниц)",
            font_size=10, color=GRAY_B
        ).next_to(mmu_title, DOWN, buff=0.08)

        cpu_mmu_unit = VGroup(cpu_box, cpu_lbl, mmu_box, mmu_title, lookup_status)
        cpu_mmu_unit.move_to([0, -2.0, 0])

        # -------------------------------------------------------------
        # 6. Текстовая строка пояснений в самом низу
        # -------------------------------------------------------------
        step_desc = Text(
            "MMU внутри ЦП транслирует виртуальные адреса процессов в физические адреса RAM",
            font_size=12,
            color=GRAY_A
        ).to_edge(DOWN, buff=0.18)

        # -------------------------------------------------------------
        # 7. СТРОГО ОРТОГОНАЛЬНЫЕ СТРЕЛКИ (Собственный цвет для каждого процесса)
        # -------------------------------------------------------------

        # --- Маршрут Notepad (ГОЛУБОЙ / NOTEPAD_COLOR): Вход в MMU и Выход в RAM ---
        p_np_start = np_cells[0][0].get_left()
        p_mmu_left_in = mmu_box.get_left() + DOWN * 0.12
        left_outer_x = -6.45

        ortho_np_to_mmu = create_ortho_arrow([
            p_np_start,
            np.array([left_outer_x, p_np_start[1], 0]),
            np.array([left_outer_x, p_mmu_left_in[1], 0]),
            p_mmu_left_in
        ], color=NOTEPAD_COLOR)

        p_mmu_left_out = mmu_box.get_left() + UP * 0.18
        p_ram_np_in = ram_cells[4][0].get_left()
        mid_left_channel_x = -2.35

        ortho_mmu_to_ram_np = create_ortho_arrow([
            p_mmu_left_out,
            np.array([mid_left_channel_x, p_mmu_left_out[1], 0]),
            np.array([mid_left_channel_x, p_ram_np_in[1], 0]),
            p_ram_np_in
        ], color=NOTEPAD_COLOR)

        # --- Маршрут MyApp (ОРАНЖЕВО-ЗОЛОТОЙ / MYAPP_COLOR): Вход в MMU и Выход в RAM ---
        p_my_start = my_cells[0][0].get_right()
        p_mmu_right_in = mmu_box.get_right() + DOWN * 0.12
        right_outer_x = 6.45

        ortho_my_to_mmu = create_ortho_arrow([
            p_my_start,
            np.array([right_outer_x, p_my_start[1], 0]),
            np.array([right_outer_x, p_mmu_right_in[1], 0]),
            p_mmu_right_in
        ], color=MYAPP_COLOR)

        p_mmu_right_out = mmu_box.get_right() + UP * 0.18
        p_ram_my_in = ram_cells[1][0].get_right()
        mid_right_channel_x = 2.35

        ortho_mmu_to_ram_my = create_ortho_arrow([
            p_mmu_right_out,
            np.array([mid_right_channel_x, p_mmu_right_out[1], 0]),
            np.array([mid_right_channel_x, p_ram_my_in[1], 0]),
            p_ram_my_in
        ], color=MYAPP_COLOR)

        # -------------------------------------------------------------
        # Сценарий анимации
        # -------------------------------------------------------------
        self.play(FadeIn(notepad_col), FadeIn(myapp_col), run_time=0.9)
        self.play(FadeIn(ram_col), Create(ram_stick), run_time=0.9)
        self.play(FadeIn(cpu_mmu_unit), FadeIn(step_desc), run_time=0.8)
        self.wait(0.5)

        # Шаг 1: Notepad.exe (Голубой поток)
        np_lookup_lbl = Text(
            "Lookup Table (Notepad): 0x7F793950000 -> 0xBC650000",
            font_size=9, color=NOTEPAD_COLOR
        ).move_to(lookup_status.get_center())
        np_info = Text(
            "1. Запрос Notepad.exe поступает в MMU процессора",
            font_size=12, color=NOTEPAD_COLOR
        ).to_edge(DOWN, buff=0.18)

        self.play(Transform(step_desc, np_info), Create(ortho_np_to_mmu), run_time=1.0)
        self.play(
            mmu_box.animate.set_stroke(NOTEPAD_COLOR, 2.5),
            Transform(lookup_status, np_lookup_lbl),
            run_time=0.5
        )

        np_to_ram_info = Text(
            "2. MMU направляет запрос Notepad.exe в физический адрес 0xBC650000",
            font_size=12, color=NOTEPAD_COLOR
        ).to_edge(DOWN, buff=0.18)
        self.play(Transform(step_desc, np_to_ram_info), Create(ortho_mmu_to_ram_np), run_time=1.0)
        self.play(ram_cells[4][0].animate.set_stroke(WHITE, 3.2), run_time=0.4)
        self.play(ram_cells[4][0].animate.set_stroke(NOTEPAD_COLOR, 2.8), run_time=0.3)
        self.wait(0.7)

        # Шаг 2: MyApp.exe (Оранжево-золотой поток)
        my_lookup_lbl = Text(
            "Lookup Table (MyApp): 0x7F793950000 -> 0x33CE0000",
            font_size=9, color=MYAPP_COLOR
        ).move_to(lookup_status.get_center())
        my_info = Text(
            "3. Запрос MyApp.exe поступает MMU процессора",
            font_size=12, color=MYAPP_COLOR
        ).to_edge(DOWN, buff=0.18)

        self.play(Transform(step_desc, my_info), Create(ortho_my_to_mmu), run_time=1.0)
        self.play(
            mmu_box.animate.set_stroke(MYAPP_COLOR, 2.5),
            Transform(lookup_status, my_lookup_lbl),
            run_time=0.5
        )

        my_to_ram_info = Text(
            "4. MMU направляет запрос MyApp.exe в физический адрес 0x33CE0000",
            font_size=12, color=MYAPP_COLOR
        ).to_edge(DOWN, buff=0.18)
        self.play(Transform(step_desc, my_to_ram_info), Create(ortho_mmu_to_ram_my), run_time=1.0)
        self.play(ram_cells[1][0].animate.set_stroke(WHITE, 3.2), run_time=0.4)
        self.play(ram_cells[1][0].animate.set_stroke(MYAPP_COLOR, 2.8), run_time=0.3)

        # Финальное резюме
        final_info = Text(
            "MMU в составе ЦП изолирует память процессов: Notepad.exe -> 0xBC650000, MyApp.exe -> 0x33CE0000",
            font_size=11,
            color=WHITE
        ).to_edge(DOWN, buff=0.18)
        self.play(
            mmu_box.animate.set_stroke(TEAL_C, 2),
            Transform(step_desc, final_info),
            run_time=0.8
        )

        self.wait(3.0)