from datetime import date, timedelta

import pytest

def _create_task(client, **overrides):
    payload = {
        "title": "Write unit tests",
        "description": "Cover CRUD endpoints",
        "status": "pending",
        "priority": "high",
        "assigned_to": "alice@example.com",
        "tags": ["testing", "backend"],
        "due_date": None,
    }
    payload.update(overrides)
    return client.post("/tasks", json=payload)


class TestTaskSchemaValidation:
    def test_task_create_rejects_too_many_tags(self):
        from app.models import TaskCreate

        tags = [f"tag-{i}" for i in range(21)]

        with pytest.raises(ValueError):
            TaskCreate(title="Too many tags", tags=tags)

    def test_task_create_trims_and_validates_tags(self):
        from app.models import TaskCreate

        task = TaskCreate(title="Tag cleanup", tags=["  alpha  ", "beta"])

        assert task.tags == ["alpha", "beta"]

    def test_task_update_allows_partial_payload_with_tags(self):
        from app.models import TaskUpdate

        update = TaskUpdate(tags=["done"])

        assert update.model_dump(exclude_unset=True) == {"tags": ["done"]}


class TestCreateTask:
    def test_create_task_success(self, client):
        response = _create_task(client)
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Write unit tests"
        assert body["status"] == "pending"
        assert body["priority"] == "high"
        assert body["assigned_to"] == "alice@example.com"
        assert "id" in body
        assert "created_at" in body

    def test_create_task_without_assigned_to_defaults_to_none(self, client):
        response = _create_task(client, assigned_to=None)
        assert response.status_code == 201
        assert response.json()["assigned_to"] is None

    def test_create_task_missing_title_returns_400(self, client):
        response = client.post("/tasks", json={"description": "no title"})
        assert response.status_code == 400

    def test_create_task_blank_title_returns_400(self, client):
        response = _create_task(client, title="")
        assert response.status_code == 400

    def test_create_task_invalid_status_returns_400(self, client):
        response = _create_task(client, status="not_a_status")
        assert response.status_code == 400

    def test_create_task_invalid_priority_returns_400(self, client):
        response = _create_task(client, priority="urgent")
        assert response.status_code == 400

    def test_create_task_with_tags(self, client):
        response = _create_task(client, tags=["urgent", "review"])
        assert response.status_code == 201
        assert response.json()["tags"] == ["urgent", "review"]

    def test_create_task_without_tags_defaults_to_empty_list(self, client):
        response = _create_task(client, tags=[])
        assert response.status_code == 201
        assert response.json()["tags"] == []

    def test_create_task_rejects_tag_overflow(self, client):
        response = _create_task(client, tags=[f"tag-{i}" for i in range(21)])
        assert response.status_code == 400

    def test_create_task_accepts_today_due_date(self, client):
        due_date = date.today().isoformat()
        response = _create_task(client, due_date=due_date)

        assert response.status_code == 201
        assert response.json()["due_date"] == due_date

    def test_create_task_accepts_future_due_date(self, client):
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = _create_task(client, due_date=due_date)

        assert response.status_code == 201
        assert response.json()["due_date"] == due_date

    def test_create_task_without_due_date_defaults_to_none(self, client):
        response = _create_task(client)

        assert response.status_code == 201
        assert response.json()["due_date"] is None

    def test_create_task_rejects_past_due_date(self, client):
        due_date = (date.today() - timedelta(days=1)).isoformat()
        response = _create_task(client, due_date=due_date)

        assert response.status_code == 400

    def test_create_task_rejects_malformed_due_date(self, client):
        response = _create_task(client, due_date="not-a-date")

        assert response.status_code == 400


class TestGetTasks:
    def test_get_all_tasks_empty(self, client):
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_tasks_returns_created_tasks(self, client):
        _create_task(client, title="Task 1")
        _create_task(client, title="Task 2")
        response = client.get("/tasks")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_all_tasks_filter_by_status(self, client):
        _create_task(client, title="Pending task", status="pending")
        _create_task(client, title="Done task", status="completed")
        response = client.get("/tasks", params={"status": "completed"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["title"] == "Done task"

    def test_get_all_tasks_filter_by_assigned_to(self, client):
        _create_task(client, title="Alice task", assigned_to="alice@example.com")
        _create_task(client, title="Bob task", assigned_to="bob@example.com")
        response = client.get("/tasks", params={"assigned_to": "bob@example.com"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["title"] == "Bob task"

    def test_get_all_tasks_filter_by_status_invalid_returns_400(self, client):
        response = client.get("/tasks", params={"status": "blocked"})
        assert response.status_code == 400

    def test_get_task_by_id_success(self, client):
        created = _create_task(client).json()
        response = client.get(f"/tasks/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_task_by_id_not_found_returns_404(self, client):
        response = client.get("/tasks/9999")
        assert response.status_code == 404


class TestUpdateTask:
    def test_update_task_success(self, client):
        created = _create_task(client).json()
        response = client.put(
            f"/tasks/{created['id']}",
            json={"status": "in_progress", "title": "Updated title"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "in_progress"
        assert body["title"] == "Updated title"
        assert body["description"] == created["description"]

    def test_update_task_not_found_returns_404(self, client):
        response = client.put("/tasks/9999", json={"title": "Nope"})
        assert response.status_code == 404

    def test_update_task_assigns_user(self, client):
        created = _create_task(client, assigned_to=None).json()
        response = client.put(f"/tasks/{created['id']}", json={"assigned_to": "carol@example.com"})
        assert response.status_code == 200
        assert response.json()["assigned_to"] == "carol@example.com"

    def test_update_task_reassigns_user(self, client):
        created = _create_task(client, assigned_to="alice@example.com").json()
        response = client.put(f"/tasks/{created['id']}", json={"assigned_to": "bob@example.com"})
        assert response.status_code == 200
        assert response.json()["assigned_to"] == "bob@example.com"

    def test_update_task_clears_assigned_to(self, client):
        created = _create_task(client, assigned_to="alice@example.com").json()
        response = client.put(f"/tasks/{created['id']}", json={"assigned_to": None})
        assert response.status_code == 200
        assert response.json()["assigned_to"] is None

    def test_update_task_empty_body_returns_400(self, client):
        created = _create_task(client).json()
        response = client.put(f"/tasks/{created['id']}", json={})
        assert response.status_code == 400

    def test_update_task_invalid_status_returns_400(self, client):
        created = _create_task(client).json()
        response = client.put(f"/tasks/{created['id']}", json={"status": "bogus"})
        assert response.status_code == 400

    def test_update_task_update_tags(self, client):
        created = _create_task(client, tags=["old"]).json()
        response = client.put(f"/tasks/{created['id']}", json={"tags": ["new", "tags"]})
        assert response.status_code == 200
        assert response.json()["tags"] == ["new", "tags"]

    def test_update_task_clear_tags(self, client):
        created = _create_task(client, tags=["old"]).json()
        response = client.put(f"/tasks/{created['id']}", json={"tags": []})
        assert response.status_code == 200
        assert response.json()["tags"] == []

    def test_update_task_allows_tags_only(self, client):
        created = _create_task(client, tags=["old"]).json()
        response = client.put(f"/tasks/{created['id']}", json={"tags": ["fresh"]})
        assert response.status_code == 200
        assert response.json()["tags"] == ["fresh"]

    def test_update_task_sets_and_replaces_due_date(self, client):
        created = _create_task(client).json()
        first_due_date = (date.today() + timedelta(days=3)).isoformat()
        second_due_date = (date.today() + timedelta(days=10)).isoformat()

        first_response = client.put(
            f"/tasks/{created['id']}", json={"due_date": first_due_date}
        )
        second_response = client.put(
            f"/tasks/{created['id']}", json={"due_date": second_due_date}
        )

        assert first_response.status_code == 200
        assert first_response.json()["due_date"] == first_due_date
        assert second_response.status_code == 200
        assert second_response.json()["due_date"] == second_due_date

    def test_update_task_clears_due_date_with_null(self, client):
        due_date = (date.today() + timedelta(days=3)).isoformat()
        created = _create_task(client, due_date=due_date).json()

        response = client.put(
            f"/tasks/{created['id']}", json={"due_date": None}
        )

        assert response.status_code == 200
        assert response.json()["due_date"] is None

    def test_update_task_omitting_due_date_preserves_value(self, client):
        due_date = (date.today() + timedelta(days=3)).isoformat()
        created = _create_task(client, due_date=due_date).json()

        response = client.put(
            f"/tasks/{created['id']}", json={"title": "Updated title"}
        )

        assert response.status_code == 200
        assert response.json()["due_date"] == due_date
        assert response.json()["title"] == "Updated title"

    def test_update_task_rejects_malformed_due_date(self, client):
        created = _create_task(client).json()

        response = client.put(
            f"/tasks/{created['id']}", json={"due_date": "not-a-date"}
        )

        assert response.status_code == 400

    def test_update_task_due_date_not_found_returns_404(self, client):
        response = client.put(
            "/tasks/9999", json={"due_date": date.today().isoformat()}
        )

        assert response.status_code == 404


class TestDueDateFilter:
    def test_filter_due_before_excludes_equal_later_and_undated_tasks(self, client):
        cutoff = date.today() + timedelta(days=10)
        _create_task(client, title="Before", due_date=(cutoff - timedelta(days=1)).isoformat())
        _create_task(client, title="Equal", due_date=cutoff.isoformat())
        _create_task(client, title="After", due_date=(cutoff + timedelta(days=1)).isoformat())
        _create_task(client, title="Undated")

        response = client.get("/tasks", params={"due_before": cutoff.isoformat()})

        assert response.status_code == 200
        assert [task["title"] for task in response.json()] == ["Before"]

    def test_filter_due_before_returns_empty_when_no_tasks_match(self, client):
        cutoff = date.today()
        _create_task(client, due_date=cutoff.isoformat())

        response = client.get("/tasks", params={"due_before": cutoff.isoformat()})

        assert response.status_code == 200
        assert response.json() == []

    def test_filter_due_before_rejects_invalid_date(self, client):
        response = client.get("/tasks", params={"due_before": "not-a-date"})

        assert response.status_code == 400

    def test_filter_due_before_composes_with_existing_filters(self, client):
        cutoff = date.today() + timedelta(days=10)
        _create_task(
            client,
            title="Matching task",
            assigned_to="bob@example.com",
            status="completed",
            due_date=(cutoff - timedelta(days=1)).isoformat(),
        )
        _create_task(
            client,
            title="Wrong assignee",
            assigned_to="alice@example.com",
            status="completed",
            due_date=(cutoff - timedelta(days=1)).isoformat(),
        )

        response = client.get(
            "/tasks",
            params={
                "due_before": cutoff.isoformat(),
                "status": "completed",
                "assigned_to": "bob@example.com",
            },
        )

        assert response.status_code == 200
        assert [task["title"] for task in response.json()] == ["Matching task"]


class TestDeleteTask:
    def test_delete_task_success(self, client):
        created = _create_task(client).json()
        response = client.delete(f"/tasks/{created['id']}")
        assert response.status_code == 204

        get_response = client.get(f"/tasks/{created['id']}")
        assert get_response.status_code == 404

    def test_delete_task_not_found_returns_404(self, client):
        response = client.delete("/tasks/9999")
        assert response.status_code == 404


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
