function formatarHora(dateObj) {
  return dateObj?.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

document.addEventListener("DOMContentLoaded", () => {
  iniciarCalendario();
});

function iniciarCalendario() {
  var calendarEl = document.getElementById("calendario");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "timeGridDay",
    locale: "pt-BR",
    allDaySlot: false,
    selectMirror: false,
    selectLongPressDelay: 300,
    eventLongPressDelay: 1,
    eventMinHeight: 40,
    selectable: true,
    initialDate: new Date(),
    slotLabelFormat: {
      hour: "2-digit", // Use 2-digit format for hours (e.g., "01", "02", ..., "12")
      minute: "2-digit", // Use 2-digit format for minutes (e.g., "00", "15", "30", "45")
      omitZeroMinute: false, // Keep minutes with leading zero (e.g., "01:00" instead of "1:00")
      hour12: false, // Use 24-hour format (e.g., "00:00" to "23:00")
    },
    headerToolbar: false,
    slotMinTime: "7:00:00",
    slotMaxTime: "22:00:00",
    events: [
      {
        title: "Reserva de teste 1",
        start: "2023-09-02T09:00:00",
        end: "2023-09-02T10:45:00",
        class: "reserva_encerrada"
      },
      {
        title: "Reserva de teste 3",
        start: "2023-09-02T12:00:00",
        end: "2023-09-02T13:00:00",
        class: "reserva_andamento"
      },
      {
        title: "Reserva de teste 3",
        start: "2023-09-02T14:00:00",
        end: "2023-09-02T15:30:00",
        class: "reserva_reservada"
      },
      {
        title: "Reserva de teste 4",
        start: "2023-09-02T16:58:00",
        end: "2023-09-02T17:30:00",
        class: "reserva_reservada"
      },
    ],
    eventContent: (arg) => ({
      html: `
        <a 
          class="d-flex flex-column h-100 px-1 w-100 text-light" 
          style="text-decoration:none;"
        >

        <div style="flex:1 1 auto;"><b>${arg.event.title}</b></div>

        <div class="d-flex justify-content-end">
          ${formatarHora(arg.event.start)} - ${formatarHora(arg.event.end)}
        </div>

      </a>`,
    }),
    select: onSelect,
  });

  function onSelect(arg) {
    try {
      const reservas = calendar.getEvents();
      let start = null;
      let end = null;
      for (const reserva of reservas) {
        if (
          start === null &&
          reserva.start <= arg.start &&
          arg.start <= reserva.end
        ) {
          // incrementa um minuto
          start = new Date(reserva.end.getTime() + 60000);
        }
        if (
          end === null &&
          reserva.start <= arg.end &&
          arg.end <= reserva.end
        ) {
          // decrementa um minuto
          end = new Date(reserva.start.getTime() - 60000);
        }
      }
      if (end === null) {
        end = arg.end;
      }
      if (start === null) {
        start = arg.start;
      }
      if (end > start) {
        document.getElementById(
          "id_horario_inicio"
        ).value = start.toLocaleTimeString();
        console.log("abriria o modal");
        // document
        $("#cadastro").modal("show");
      }
    } catch (e) {
      console.log("erro ao abrir modal ", e);
    }
  }

  calendar.render();
}